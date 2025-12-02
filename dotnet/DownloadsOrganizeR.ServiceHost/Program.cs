using System.Diagnostics;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace DownloadsOrganizeR.ServiceHost
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var builder = Host.CreateApplicationBuilder(args);

            // Enable Windows Service hosting
            builder.Services.AddWindowsService(options =>
            {
                options.ServiceName = "DownloadsOrganizer";
            });

            builder.Logging.ClearProviders();
            builder.Logging.AddEventLog();
            builder.Services.AddHostedService<PythonProcessWorker>();

            var host = builder.Build();
            host.Run();
        }
    }

    public class PythonProcessWorker : BackgroundService
    {
        private readonly ILogger<PythonProcessWorker> _logger;
        private readonly IConfiguration _config;
        private Process? _process;

        public PythonProcessWorker(ILogger<PythonProcessWorker> logger, IConfiguration config)
        {
            _logger = logger;
            _config = config;
        }

        protected override Task ExecuteAsync(CancellationToken stoppingToken)
        {
            _ = Task.Run(() => RunLoop(stoppingToken), stoppingToken);
            return Task.CompletedTask;
        }

        private void RunLoop(CancellationToken token)
        {
            var pythonExe = _config["PythonExe"] ?? "python";
            var scriptPath = _config["ScriptPath"] ?? "Organizer.py";
            var workingDir = _config["WorkingDirectory"] ?? AppContext.BaseDirectory;
            var restartOnExit = bool.TryParse(_config["RestartOnExit"], out var r) ? r : true;
            var restartDelayMs = int.TryParse(_config["RestartDelayMs"], out var d) ? d : 5000;

            Directory.CreateDirectory(Path.Combine(workingDir, "service-logs"));
            var stdoutPath = Path.Combine(workingDir, "service-logs", "organizer_stdout.log");
            var stderrPath = Path.Combine(workingDir, "service-logs", "organizer_stderr.log");

            while (!token.IsCancellationRequested)
            {
                try
                {
                    var psi = new ProcessStartInfo
                    {
                        FileName = pythonExe,
                        Arguments = scriptPath,
                        WorkingDirectory = workingDir,
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        CreateNoWindow = true
                    };

                    _logger.LogInformation("Starting Python service: {exe} {script}", pythonExe, scriptPath);
                    _process = Process.Start(psi);
                    if (_process == null)
                    {
                        _logger.LogError("Failed to start Python process.");
                        break;
                    }

                    using var stdout = new StreamWriter(stdoutPath, append: true);
                    using var stderr = new StreamWriter(stderrPath, append: true);

                    _ = Task.Run(async () =>
                    {
                        var so = _process.StandardOutput;
                        char[] buf = new char[4096];
                        int n;
                        while ((n = await so.ReadAsync(buf, 0, buf.Length)) > 0 && !token.IsCancellationRequested)
                        {
                            await stdout.WriteAsync(buf, 0, n);
                            await stdout.FlushAsync();
                        }
                    }, token);

                    _ = Task.Run(async () =>
                    {
                        var se = _process.StandardError;
                        char[] buf = new char[4096];
                        int n;
                        while ((n = await se.ReadAsync(buf, 0, buf.Length)) > 0 && !token.IsCancellationRequested)
                        {
                            await stderr.WriteAsync(buf, 0, n);
                            await stderr.FlushAsync();
                        }
                    }, token);

                    _process.WaitForExit();
                    _logger.LogWarning("Python process exited with code {code}", _process.ExitCode);
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error running Python process");
                }

                if (!restartOnExit || token.IsCancellationRequested)
                    break;

                _logger.LogInformation("Restarting in {delay} ms...", restartDelayMs);
                Task.Delay(restartDelayMs, token).Wait(token);
            }
        }

        public override Task StopAsync(CancellationToken cancellationToken)
        {
            try
            {
                if (_process != null && !_process.HasExited)
                {
                    _process.Kill(entireProcessTree: true);
                    _process.Dispose();
                }
            }
            catch { }
            return base.StopAsync(cancellationToken);
        }
    }
}
