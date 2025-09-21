async function log(msg) {
  let el = document.getElementById('log');
  el.textContent = `${new Date().toISOString()}  ${msg}\n` + el.textContent;
}

async function fetchDisks() {
  const r = await fetch('/api/v1/disks');
  const j = await r.json();
  document.getElementById('allowed').textContent = j.allowed_prefixes.join(', ');
  const tbody = document.querySelector('#disks tbody');
  tbody.innerHTML = '';
  for (const d of j.devices) {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${d.name}</td><td>${d.device}</td><td>${d.size}</td><td>${d.mountpoint || ''}</td>`;
    const actionsTd = document.createElement('td');

    const unBtn = document.createElement('button');
    unBtn.textContent = 'Отмонтировать';
    unBtn.onclick = async () => {
      await opPost('/api/v1/disks/unmount', {device: d.device});
    };

    const mountBtn = document.createElement('button');
    mountBtn.textContent = 'Примонтировать';
    mountBtn.onclick = async () => {
      const mp = prompt("Укажите директорию для монтирования (например /mnt/test):", "/mnt/test");
      if (!mp) return;
      await opPost('/api/v1/disks/mount', {device: d.device, mount_point: mp});
    };

    const fmtBtn = document.createElement('button');
    fmtBtn.textContent = 'Форматировать';
    fmtBtn.onclick = async () => {
      if (!confirm(`Форматировать ${d.device}? Это уничтожит данные!`)) return;
      const fst = prompt("Тип файловой системы (ext4, xfs...):", "ext4");
      if (!fst) return;
      await opPost('/api/v1/disks/format', {device: d.device, fstype: fst});
    };

    actionsTd.appendChild(unBtn);
    actionsTd.appendChild(mountBtn);
    actionsTd.appendChild(fmtBtn);
    tr.appendChild(actionsTd);
    tbody.appendChild(tr);
  }
}

async function opPost(url, data) {
  const r = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  const j = await r.json();
  await log(`${url} => code ${j.returncode} stdout:${j.stdout} stderr:${j.stderr}`);
  await fetchDisks();
}

document.getElementById('refresh').addEventListener('click', fetchDisks);
window.addEventListener('load', fetchDisks);
