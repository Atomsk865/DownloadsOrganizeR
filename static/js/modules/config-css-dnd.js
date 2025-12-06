// CSS Grid drag-and-drop with animated panel movement for config modules
// Uses HTML5 drag events and a FLIP-style animation when reordering.

const STORAGE_KEY = 'configCssLayout';
const DRAG_STATE = new Map();

function getModuleOrder(grid) {
  return Array.from(grid.querySelectorAll('.config-module')).map((m) => m.dataset.module);
}

function saveOrder(grid) {
  const order = getModuleOrder(grid);
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(order));
  } catch (e) {
    console.warn('Could not save layout', e);
  }
}

function loadOrder(grid) {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const order = JSON.parse(raw);
    order.forEach((id) => {
      const el = grid.querySelector(`.config-module[data-module="${id}"]`);
      if (el) grid.appendChild(el);
    });
  } catch (e) {
    console.warn('Could not load layout', e);
  }
}

function snapshotPositions(modules) {
  const rects = new Map();
  modules.forEach((m) => {
    rects.set(m, m.getBoundingClientRect());
  });
  return rects;
}

function animateReorder(modules, beforeRects) {
  modules.forEach((m) => {
    // Skip the actively dragged module to avoid jitter
    if (m.classList.contains('dragging')) return;

    const first = beforeRects.get(m);
    const last = m.getBoundingClientRect();
    if (!first || !last) return;
    const dx = first.left - last.left;
    const dy = first.top - last.top;
    if (dx !== 0 || dy !== 0) {
      m.style.transition = 'none';
      m.style.transform = `translate(${dx}px, ${dy}px)`;
      requestAnimationFrame(() => {
        m.style.transition = 'transform 180ms ease';
        m.style.transform = 'translate(0, 0)';
      });
    }
  });
}

function getDragAfterElement(grid, y) {
  const modules = [...grid.querySelectorAll('.config-module:not(.dragging)')];
  return modules.reduce(
    (closest, child) => {
      const box = child.getBoundingClientRect();
      const offset = y - box.top - box.height / 2;
      if (offset < 0 && offset > closest.offset) {
        return { offset, element: child };
      }
      return closest;
    },
    { offset: Number.NEGATIVE_INFINITY, element: null }
  ).element;
}

function applyDragState(module, enabled) {
  const toggle = module.querySelector('.drag-toggle');
  const icon = toggle?.querySelector('i');
  const isEnabled = Boolean(enabled);

  DRAG_STATE.set(module.dataset.module, isEnabled);
  module.dataset.dragEnabled = isEnabled ? 'true' : 'false';
  module.setAttribute('draggable', isEnabled ? 'true' : 'false');

  if (toggle) {
    toggle.classList.toggle('undocked', isEnabled);
    toggle.classList.toggle('docked', !isEnabled);
    toggle.title = isEnabled ? 'Click to lock module (dock)' : 'Click to unlock module (undock)';
  }

  if (icon) {
    icon.classList.toggle('bi-pin-angle', isEnabled);
    icon.classList.toggle('bi-pin-angle-fill', !isEnabled);
  }
}

function setupPushpins(modules) {
  modules.forEach((module) => {
    const toggle = module.querySelector('.drag-toggle');
    if (!toggle) return;

    // Default to docked/locked on load
    applyDragState(module, false);

    toggle.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();

      const current = module.dataset.dragEnabled === 'true';
      applyDragState(module, !current);
    });
  });
}

export function initCssDragDrop() {
  const grid = document.getElementById('config-grid');
  if (!grid) return;

  const modules = Array.from(grid.querySelectorAll('.config-module'));
  if (!modules.length) return;

  loadOrder(grid);
  setupPushpins(modules);

  let placeholder = document.createElement('div');
  placeholder.className = 'config-placeholder';

  modules.forEach((module) => {
    // Respect initial docked state (draggable only when unlocked)
    const dragEnabled = module.dataset.dragEnabled === 'true';
    module.setAttribute('draggable', dragEnabled ? 'true' : 'false');

    module.addEventListener('dragstart', (e) => {
      // Ignore drag attempts when locked
      if (module.dataset.dragEnabled !== 'true') {
        e.preventDefault();
        return;
      }

      module.classList.add('dragging');
      placeholder.style.height = `${module.offsetHeight}px`;
      placeholder.style.minHeight = `${module.offsetHeight}px`;
      e.dataTransfer.effectAllowed = 'move';
      const img = document.createElement('div');
      e.dataTransfer.setDragImage(img, 0, 0);
    });

    module.addEventListener('dragend', () => {
      module.classList.remove('dragging');
      placeholder.remove();
      saveOrder(grid);
    });
  });

  grid.addEventListener('dragover', (e) => {
    e.preventDefault();
    const afterElement = getDragAfterElement(grid, e.clientY);
    const dragging = grid.querySelector('.config-module.dragging');
    if (!dragging) return;

    const beforeRects = snapshotPositions(Array.from(grid.children).filter((n) => n.classList.contains('config-module')));

    if (afterElement == null) {
      grid.appendChild(placeholder);
    } else {
      grid.insertBefore(placeholder, afterElement);
    }

    if (placeholder.parentElement && dragging !== placeholder) {
      grid.insertBefore(dragging, placeholder);
    }

    const modulesNow = Array.from(grid.querySelectorAll('.config-module'));
    animateReorder(modulesNow, beforeRects);
  });

  grid.addEventListener('drop', (e) => {
    e.preventDefault();
    const dragging = grid.querySelector('.config-module.dragging');
    if (dragging && placeholder.parentElement) {
      grid.insertBefore(dragging, placeholder);
    }
    placeholder.remove();
    saveOrder(grid);
  });
}

// Auto-init when imported on the config page
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => initCssDragDrop());
  } else {
    initCssDragDrop();
  }
}
