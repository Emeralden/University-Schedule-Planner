
    // ----------------- STATE -----------------
    let professors = [];
    let rooms = [];
    let courses = [];
    let time_slots = [];
    let time_slot_counter = 1;

    const $ = (id) => document.getElementById(id);
    const statusDiv = $("status");

    // =====================================================
    //  RENDER LISTS PANEL
    // =====================================================
    function renderLists() {
        // ----- Professors -----
        const pl = $("professor-list");
        pl.innerHTML = "";
        if (professors.length === 0) {
            pl.innerHTML = "<i></i>";
        } else {
            professors.forEach((p, i) => {
                const div = document.createElement("div");
                div.style.marginBottom = "10px";
                div.innerHTML = `
                    <strong>${p.name}</strong><br>
                    Unavail: [${(p.unavailable_slots || []).join(", ")}]<br>
                    Preferred: [${(p.preferred_slots || []).join(", ")}]<br>
                    Hated: [${(p.hates_slots || []).join(", ")}]<br>
                    <button class="delete-prof" data-index="${i}">Delete</button>
                    <hr>
                `;
                pl.appendChild(div);
            });
        }

        // ----- Rooms -----
        const rl = $("room-list");
        rl.innerHTML = "";
        if (rooms.length === 0) {
            rl.innerHTML = "<i></i>";
        } else {
            rooms.forEach((r, i) => {
                const div = document.createElement("div");
                div.innerHTML = `
                    ${r.name} — cap ${r.capacity}
                    <button class="delete-room" data-index="${i}">Delete</button>
                `;
                rl.appendChild(div);
            });
        }

        // ----- Time Slots -----
        const tl = $("timeslot-list");
        tl.innerHTML = "";
        if (time_slots.length === 0) {
            tl.innerHTML = "<i></i>";
        } else {
            time_slots.forEach((s, i) => {
                const div = document.createElement("div");
                div.innerHTML = `
                    Slot ${s.slot_id}: ${s.day} ${s.start_time}-${s.end_time}
                    <button class="delete-slot" data-index="${i}">Delete</button>
                `;
                tl.appendChild(div);
            });
        }

        // ----- Courses -----
        const cl = $("course-list");
        cl.innerHTML = "";
        if (courses.length === 0) {
            cl.innerHTML = "<i></i>";
        } else {
            courses.forEach((c, i) => {
                const div = document.createElement("div");
                div.innerHTML = `
                    ${c.name} — Prof ${c.professor}, Enroll ${c.enrollment}, Dept ${c.department}
                    <button class="delete-course" data-index="${i}">Delete</button>
                `;
                cl.appendChild(div);
            });
        }

        refreshProfessorSelect();
    }

    // =====================================================
    //  PROFESSOR DROPDOWN REFRESH
    // =====================================================
    function refreshProfessorSelect() {
        const sel = $("course-prof");
        if (!sel) return;
        sel.innerHTML = `<option value="" disabled selected>Select professor</option>`;
        professors.forEach((p) => {
            const o = document.createElement("option");
            o.value = p.name;
            o.innerText = p.name;
            sel.appendChild(o);
        });
    }

    // =====================================================
    //  CRUD (Add)
// =====================================================
    function addProfessor() {
        const nameEl = $("prof-name");
        const unavailEl = $("prof-unavail");
        const prefEl = $("prof-preferred");
        const hateEl = $("prof-hated");

        const name = nameEl.value.trim();
        if (!name) {
            alert("Enter professor name");
            return;
        }

        const parseSlots = (txt) =>
            txt
                ? txt.split(",")
                      .map((x) => x.trim())
                      .filter((x) => x !== "")
                      .map((x) => Number(x))
                      .filter((n) => !Number.isNaN(n))
                : [];

        professors.push({
            name,
            unavailable_slots: parseSlots(unavailEl.value),
            preferred_slots: parseSlots(prefEl.value),
            hates_slots: parseSlots(hateEl.value),
        });

        nameEl.value = "";
        unavailEl.value = "";
        prefEl.value = "";
        hateEl.value = "";

        renderLists();
    }

    function addRoom() {
        const nameEl = $("room-name");
        const capEl = $("room-cap");

        const name = nameEl.value.trim();
        const cap = Number(capEl.value);

        if (!name || !cap || Number.isNaN(cap)) {
            alert("Enter valid room data");
            return;
        }

        rooms.push({
            name,
            capacity: cap,
            unavailable_slots: [],
        });

        nameEl.value = "";
        capEl.value = "";

        renderLists();
    }

    function addCourse() {
        const nameEl = $("course-name");
        const enrollEl = $("course-enroll");
        const profSel = $("course-prof");
        const deptEl = $("course-dept");

        const name = nameEl.value.trim();
        const enroll = Number(enrollEl.value);
        const prof = (profSel.value || "").trim();
        const dept = deptEl.value.trim();

        if (!name || !enroll || Number.isNaN(enroll) || !prof || !dept) {
            alert("All course fields are required");
            return;
        }

        courses.push({
            name,
            enrollment: enroll,
            professor: prof,
            department: dept,
            is_elective_for: [],
        });

        nameEl.value = "";
        enrollEl.value = "";
        profSel.value = "";
        deptEl.value = "";

        renderLists();
    }

    function addSlot() {
        const dayEl = $("slot-day");
        const stEl = $("slot-start");
        const enEl = $("slot-end");

        const day = dayEl.value.trim();
        const st = stEl.value.trim();
        const en = enEl.value.trim();

        if (!day || !st || !en) {
            alert("All slot fields required");
            return;
        }

        time_slots.push({
            day,
            start_time: st,
            end_time: en,
            slot_id: time_slot_counter++,
        });

        dayEl.value = "";
        stEl.value = "";
        enEl.value = "";

        renderLists();
    }

    // =====================================================
    //  LIST DELETE HANDLERS (via event delegation)
    // =====================================================
    $("professor-list").addEventListener("click", (e) => {
        if (e.target.classList.contains("delete-prof")) {
            const idx = Number(e.target.dataset.index);
            if (!Number.isNaN(idx)) {
                professors.splice(idx, 1);
                renderLists();
            }
        }
    });

    $("room-list").addEventListener("click", (e) => {
        if (e.target.classList.contains("delete-room")) {
            const idx = Number(e.target.dataset.index);
            if (!Number.isNaN(idx)) {
                rooms.splice(idx, 1);
                renderLists();
            }
        }
    });

    $("timeslot-list").addEventListener("click", (e) => {
        if (e.target.classList.contains("delete-slot")) {
            const idx = Number(e.target.dataset.index);
            if (!Number.isNaN(idx)) {
                time_slots.splice(idx, 1);
                renderLists();
            }
        }
    });

    $("course-list").addEventListener("click", (e) => {
        if (e.target.classList.contains("delete-course")) {
            const idx = Number(e.target.dataset.index);
            if (!Number.isNaN(idx)) {
                courses.splice(idx, 1);
                renderLists();
            }
        }
    });

    // =====================================================
    //  JSON FILE IMPORTS (ALL FOUR)
// =====================================================
    function loadJSON(fileInput, callback) {
        const file = fileInput.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);
                callback(data);
                renderLists();
                alert("JSON loaded successfully!");
            } catch {
                alert("Invalid JSON file.");
            }
        };
        reader.readAsText(file);
    }

    const profJson = $("prof-json");
    if (profJson) {
        profJson.addEventListener("change", () =>
            loadJSON(profJson, (data) => {
                if (!Array.isArray(data)) return alert("JSON must be an array.");
                professors = professors.concat(data);
            })
        );
    }

    const roomJson = $("room-json");
    if (roomJson) {
        roomJson.addEventListener("change", () =>
            loadJSON(roomJson, (data) => {
                if (!Array.isArray(data)) return alert("JSON must be an array.");
                rooms = rooms.concat(data);
            })
        );
    }

    const courseJson = $("course-json");
    if (courseJson) {
        courseJson.addEventListener("change", () =>
            loadJSON(courseJson, (data) => {
                if (!Array.isArray(data)) return alert("JSON must be an array.");
                courses = courses.concat(data);
            })
        );
    }

    const slotJson = $("slot-json");
    if (slotJson) {
        slotJson.addEventListener("change", () =>
            loadJSON(slotJson, (data) => {
                if (!Array.isArray(data)) return alert("JSON must be an array.");
                time_slots = time_slots.concat(data);
                if (data.length > 0) {
                    const maxSlot = Math.max(...time_slots.map((s) => s.slot_id || 0));
                    time_slot_counter = maxSlot + 1;
                }
            })
        );
    }

    $("full-json").addEventListener("change", () =>
    loadJSON($("full-json"), data => {
        if (typeof data !== "object") return alert("Invalid JSON.");

        // EXPECTING: { professors:[], rooms:[], time_slots:[], courses:[] }
        professors = Array.isArray(data.professors) ? data.professors : [];
        rooms      = Array.isArray(data.rooms)      ? data.rooms      : [];
        time_slots = Array.isArray(data.time_slots) ? data.time_slots : [];
        courses    = Array.isArray(data.courses)    ? data.courses    : [];

        // fix counter
        if (time_slots.length > 0) {
            time_slot_counter = Math.max(...time_slots.map(s => s.slot_id || 0)) + 1;
        }

        renderLists();
        alert("Full problem JSON loaded!");
        })
    );


    // =====================================================
    //  SOLVE BUTTON
    // =====================================================
    async function solve() {
        statusDiv.innerText = "Solving...";

        const problem = {
            professors,
            rooms,
            time_slots,
            courses,
        };

        try {
            const res = await fetch("/solve", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(problem),
            });

            if (!res.ok) {
                const txt = await res.text();
                statusDiv.innerText = "Server error: " + txt;
                return;
            }

            const result = await res.json();

            statusDiv.innerHTML = `
                <strong>Violations:</strong> ${result.cost} &nbsp;&nbsp;
                <strong>Desirability:</strong> ${result.happiness}
            `;

            renderViolations(result.violations || []);
            renderExplanations(result.explanation || []);
            renderGrid(result.schedule.assignments || {});

        } catch (e) {
            console.error(e);
            statusDiv.innerText = "Error: " + e.message;
        }
    }

    // =====================================================
    //  RENDER: Violations + Explanations + Timetable Grid
    // =====================================================
    function renderViolations(vios) {
        const div = $("violations");
        if (!div) return;

        div.classList.remove("hidden");
        div.innerHTML = "<h3>Violations</h3>";

        if (!vios.length) {
            div.innerHTML += `<div style="color:green;">No violations</div>`;
            return;
        }

        let html = "<ul>";
        vios.forEach((v) => (html += `<li style="color:red">${v}</li>`));
        html += "</ul>";
        div.innerHTML += html;
    }

    function renderExplanations(expls) {
        const div = $("explanations");
        if (!div) return;

        div.classList.remove("hidden");
        div.innerHTML = "<h3>Explanation</h3>";

        if (!expls.length) {
            div.innerHTML += "<div>No explanation provided.</div>";
            return;
        }

        let html = "<ol>";
        expls.forEach((e) => (html += `<li>${e}</li>`));
        html += "</ol>";
        div.innerHTML += html;
    }

    function renderGrid(assignments) {
        const grid = $("timetable-grid");
        if (!grid) return;

        grid.classList.remove("hidden");
        grid.innerHTML = "<h3>Schedule Grid</h3>";

        // Sort slots by day then by time
        const slots = [...time_slots].sort((a, b) => {
            if (a.day === b.day) {
                return a.start_time.localeCompare(b.start_time);
            }
            return a.day.localeCompare(b.day);
        });

        const rs = [...rooms];

        let html = "<table border='1'><tr><th>Room</th>";

        // Column headers (NO SLOT ID)
        slots.forEach(s => {
            html += `<th>
                ${s.day}<br>
                ${s.start_time} – ${s.end_time}
            </th>`;
        });
        html += "</tr>";

        // Rows
        rs.forEach(r => {
            html += `<tr><th>${r.name}</th>`; // NO CAPACITY

            slots.forEach(s => {
                let cell = "";
                for (const c in assignments) {
                    const [rm, sl] = assignments[c];
                    if (rm === r.name && sl === s.slot_id) {
                        cell = `
                            <div style="font-size:16px; font-weight:bold;">${c}</div>
                        `;
                    }
                }
                html += `<td style="min-width:120px;height:50px;text-align:center">${cell}</td>`;
            });

            html += "</tr>";
        });

        html += "</table>";
        grid.innerHTML = html;
    }






    // =====================================================
    //  WIRE BUTTONS
    // =====================================================
    const addSlotBtn = $("add-slot-btn");
    const addProfBtn = $("add-prof-btn");
    const addRoomBtn = $("add-room-btn");
    const addCourseBtn = $("add-course-btn");
    const solveBtn = $("solve-btn");

window.addEventListener("DOMContentLoaded", () => {
    $("add-slot-btn").addEventListener("click", e => { e.preventDefault(); addSlot(); });
    $("add-prof-btn").addEventListener("click", e => { e.preventDefault(); addProfessor(); });
    $("add-room-btn").addEventListener("click", e => { e.preventDefault(); addRoom(); });
    $("add-course-btn").addEventListener("click", e => { e.preventDefault(); addCourse(); });
    $("solve-btn").addEventListener("click", e => { e.preventDefault(); solve(); });
    renderLists();
});
