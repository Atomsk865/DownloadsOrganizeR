(function(){
    const STATUS_ENDPOINT = '/api/setup/organizer-status';
    const START_ENDPOINT = '/api/setup/start-organizer';

    function resolveTarget(target){
        if(!target){ return null; }
        if(typeof target === 'string'){ return document.getElementById(target); }
        return target;
    }

    function setStatus(el, text, tone){
        if(!el){ return; }
        const color = tone || 'muted';
        el.className = `small text-${color}`;
        el.textContent = text;
    }

    async function fetchStatus(){
        const response = await fetch(STATUS_ENDPOINT, { credentials: 'include', cache: 'no-store' });
        if(!response.ok){
            throw new Error('Unable to query organizer status');
        }
        return response.json();
    }

    function updateState(button, statusEl, data){
        const running = Boolean(data && (data.running || data.service_running));
        button.dataset.organizerRunning = running ? 'true' : 'false';
        const pid = data && data.pid ? ` (PID ${data.pid})` : '';
        if(running){
            setStatus(statusEl, `Organizer already running${pid}.`, 'success');
        } else {
            setStatus(statusEl, 'Organizer not running. Click to start it now.', 'warning');
        }
    }

    async function refreshStatus(button, statusEl){
        if(!button){ return; }
        try {
            setStatus(statusEl, 'Checking organizer status…', 'secondary');
            const data = await fetchStatus();
            updateState(button, statusEl, data);
        } catch (error) {
            setStatus(statusEl, error && error.message ? error.message : 'Status check failed.', 'danger');
            button.dataset.organizerRunning = 'unknown';
        }
    }

    async function requestStart(button, statusEl){
        if(!button){ return false; }
        const originalLabel = button.dataset.originalLabel || button.textContent || 'Start Organizer';
        button.dataset.originalLabel = originalLabel;
        button.disabled = true;
        button.textContent = 'Starting…';
        setStatus(statusEl, 'Requesting organizer start…', 'secondary');
        try {
            const response = await fetch(START_ENDPOINT, {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json().catch(()=>({}));
            if (response.ok && data && data.success) {
                const baseMsg = data.already_running ? 'Organizer is already running.' : 'Organizer started successfully.';
                const pid = data.pid ? ` (PID ${data.pid})` : '';
                setStatus(statusEl, `${baseMsg}${pid}`, 'success');
                return true;
            }
            const err = data && data.error ? data.error : 'Failed to start organizer.';
            setStatus(statusEl, err, 'danger');
        } catch (error) {
            setStatus(statusEl, error && error.message ? error.message : 'Unexpected error starting organizer.', 'danger');
        } finally {
            button.disabled = false;
            button.textContent = button.dataset.originalLabel || 'Start Organizer';
        }
        return false;
    }

    window.attachStartOrganizerButton = function(buttonTarget, statusTarget){
        const button = resolveTarget(buttonTarget);
        const statusEl = resolveTarget(statusTarget);
        if(!button){ return; }
        if(statusEl && !statusEl.className){ statusEl.className = 'small text-muted'; }

        const handleClick = async function(){
            if(button.dataset.organizerRunning === 'true'){
                setStatus(statusEl, 'Organizer already running. No action taken.', 'info');
                return;
            }
            await requestStart(button, statusEl);
            await refreshStatus(button, statusEl);
        };

        button.addEventListener('click', handleClick);
        refreshStatus(button, statusEl);
    };
})();
