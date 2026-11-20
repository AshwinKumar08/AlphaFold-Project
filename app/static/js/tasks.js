// ----------------------------- download task -----------------------------

async function downloadResult(url, taskId) {
    try {
        const res = await fetch(url);

        // Handle "result not found"
        if (res.status === 404) {
            alert(`Task ${taskId}: The result is not ready yet. Please try again later.`);
            return;
        }

        // Handle other unexpected errors
        if (!res.ok) {
            alert(`Task ${taskId}: Failed to download result (HTTP ${res.status}).`);
            return;
        }

        // Download the ZIP file
        const blob = await res.blob();
        const downloadUrl = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = `task_${taskId}_result.zip`;
        document.body.appendChild(a);
        a.click();
        a.remove();

        window.URL.revokeObjectURL(downloadUrl);

    } catch (e) {
        alert(`Task ${taskId}: Network error while downloading result.`);
    }
}



// ----------------------------- Show Task Log -----------------------------

async function showLog(url, taskId) {
    try {
        const res = await fetch(url);

        if (res.status === 404) {
            alert(`Task ${taskId}: Log file not available yet.`);
            return;
        }

        if (!res.ok) {
            alert(`Task ${taskId}: Failed to load log (HTTP ${res.status}).`);
            return;
        }

        const logText = await res.text();

        const logWindow = window.open(
            "",
            `task_${taskId}_log`,
            "width=800,height=600,scrollbars=yes"
        );

        logWindow.document.write(`
                  <html>
                    <head>
                      <title>Task ${taskId} Log</title>
                      <style>
                        body {
                          background: #0f172a;
                          color: #e5e7eb;
                          font-family: monospace;
                          padding: 16px;
                          white-space: pre-wrap;
                        }
                      </style>
                    </head>
                    <body>${logText}</body>
                  </html>
              `);

        logWindow.document.close();

    } catch (e) {
        alert(`Task ${taskId}: Network error while loading log.`);
    }
}

// ----------------------------- Enable and Disable Tasks -----------------------------

async function toggleTaskEnabled(inputEl, sessionUUID) {
    const taskId = inputEl.dataset.taskId;
    const prevChecked = inputEl.checked;
    const newEnabled = prevChecked ? 1 : 0;

    inputEl.disabled = true;

    try {
        const res = await fetch(`/api/1.0/${sessionUUID}/task/${encodeURIComponent(taskId)}/enabled`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ enabled: newEnabled }),
        });

        if (!res.ok) throw new Error("Request failed");
    } catch (e) {
        inputEl.checked = !prevChecked;
        alert("Could not update task status. Please try again.");
    } finally {
        inputEl.disabled = false;
    }
}



// ----------------------------- Delete Tasks -----------------------------

async function deleteTask(taskId, sessionUUID) {
    const confirmed = confirm("Are you sure you want to delete this task?");
    if (!confirmed) return;

    try {
        const res = await fetch(`/api/1.0/${sessionUUID}/task/${encodeURIComponent(taskId)}`, {
            method: "DELETE",
        });

        const text = await res.text();
        let data = null;
        try { data = JSON.parse(text); } catch (_) { }

        if (!res.ok) {
            const msg = (data && data.message) ? data.message : (text || `HTTP ${res.status}`);
            throw new Error(msg);
        }

        // success => refresh list
        window.location.reload();
    } catch (e) {
        alert(`Could not delete task: ${e.message}`);
    }
}


// ----------------------------- create task -----------------------------


document.addEventListener("DOMContentLoaded", () => {

    // Get the create task form
    const form = document.getElementById("createTaskForm");
    if (!form) return; // Run only on create task page

    form.addEventListener("submit", async function (e) {
        e.preventDefault(); // Prevent default HTML form submission

        // Extract sessionUUID from URL
        const parts = window.location.pathname.split("/");
        const sessionUUID = parts[2];
        const userId = document.getElementById("createpage").dataset.userid;
        const rawDate = document.getElementById("task-max_template_data").value.trim();

        // Regular expression for YYYY-MM-DD
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;

        let finalDate;

        if (rawDate === "") {
            // If empty → use today's date
            const today = new Date();
            const year = today.getFullYear();
            const month = String(today.getMonth() + 1).padStart(2, "0");
            const day = String(today.getDate()).padStart(2, "0");
            finalDate = `${year}-${month}-${day}`;
        } else {
            // If not empty → validate format
            if (!dateRegex.test(rawDate)) {
                alert("Invalid date format. Please use YYYY-MM-DD.");
                return; // stop form submission
            }

            finalDate = rawDate;
        }


        // Build request payload according to backend API
        const data = {
            userId: parseInt(userId),
            name: document.getElementById("task-name").value,
            userComment: document.getElementById("task-comment").value,
            enabled: 0,
            fasta: document.getElementById("task-fasta").value,
            modelPreset: document.getElementById("task-model_preset").value,
            fullDBS: parseInt(document.getElementById("task-full_dbs").value),
            modelsToRelax: parseInt(document.getElementById("task-models_to_relax").value),
            enableGpuRelax: document.getElementById("task-enable_gpu_relax").checked ? 1 : 0,
            maxTemplateDate: finalDate
        };

        try {
            // Send task data to backend API
            const res = await fetch(`/api/1.0/${sessionUUID}/task`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            // Handle backend error
            if (!res.ok) {
                const error = await res.json();
                alert(error.status);
                return;
            }

            // On success, redirect back to task list
            window.location.href = `/ui/${sessionUUID}/tasks`;

        } catch (err) {
            console.error(err);
            alert("Network error while creating task.");
        }
    });
});


// ----------------------------- Edit Task -----------------------------


document.addEventListener("DOMContentLoaded", async () => {

    const page = document.getElementById("editpage");
    if (!page) return;

    const sessionUUID = window.location.pathname.split("/")[2];
    const taskId = page.dataset.taskid;
    const isAdmin = page.dataset.isAdmin === "true";

    // Load task data
    let task = null;

    try {
        const res = await fetch(`/api/1.0/${sessionUUID}/task/${taskId}`);
        const data = await res.json();

        if (!res.ok || data.status !== "ok") {
            alert("Could not load task.");
            return;
        }

        task = data.task;

        // Fill fields
        document.getElementById("task-name").value = task.name || "";
        document.getElementById("task-comment").value = task.userComment || "";
        document.getElementById("task-fasta").value = task.fasta || "";
        document.getElementById("task-model_preset").value = task.model_preset || "";
        document.getElementById("task-full_dbs").value = task.full_dbs;
        document.getElementById("task-models_to_relax").value = task.models_to_relax;
        document.getElementById("task-enable_gpu_relax").checked = task.enable_gpu_relax == 1;
        document.getElementById("task-max_template_data").value = task.max_template_date || "";

    } catch (err) {
        console.error(err);
        alert("Failed to load task.");
        return;
    }

    // load owner selector for admin
    if (isAdmin) {
        const wrapper = document.getElementById("admin-owner-wrapper");
        if (wrapper) wrapper.style.display = "flex";

        try {
            const res = await fetch(`/api/1.0/${sessionUUID}/user`);
            const data = await res.json();

            if (data.status !== "ok") return;

            const select = document.getElementById("task-owner");
            select.innerHTML = "";

            data.users.forEach(u => {
                const opt = document.createElement("option");
                opt.value = u.id;
                opt.textContent = `${u.name} (id=${u.id})`;
                if (u.id === task.userId) opt.selected = true;
                select.appendChild(opt);
            });

        } catch (err) {
            console.error("Failed to load users", err);
        }
    }

    // Submit
    const form = document.getElementById("editTaskForm");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const rawDate = document.getElementById("task-max_template_data").value.trim();
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;

        let finalDate;
        if (rawDate === "") {
            const d = new Date();
            finalDate = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
        } else {
            if (!dateRegex.test(rawDate)) {
                alert("Invalid date format. Use YYYY-MM-DD.");
                return;
            }
            finalDate = rawDate;
        }

        const payload = {
            userId: task.userId,
            name: document.getElementById("task-name").value,
            userComment: document.getElementById("task-comment").value,
            fasta: document.getElementById("task-fasta").value,
            modelPreset: document.getElementById("task-model_preset").value,
            fullDBS: parseInt(document.getElementById("task-full_dbs").value),
            modelsToRelax: parseInt(document.getElementById("task-models_to_relax").value),
            enableGpuRelax: document.getElementById("task-enable_gpu_relax").checked ? 1 : 0,
            maxTemplateDate: finalDate
        };

        // admin can change owner
        if (isAdmin) {
            const ownerSelect = document.getElementById("task-owner");
            if (ownerSelect && ownerSelect.value) {
                payload.userId = parseInt(ownerSelect.value);
            }
        } else {
            payload.userId = task.userId;
        }


        try {
            const res = await fetch(`/api/1.0/${sessionUUID}/task/${taskId}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const result = await res.json();

            if (!res.ok || result.status !== "success") {
                alert(result.message || "Update failed");
                return;
            }

            window.location.href = `/ui/${sessionUUID}/tasks`;

        } catch (err) {
            console.error(err);
            alert("Network error while updating task.");
        }
    });

});


