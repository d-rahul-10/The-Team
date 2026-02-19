// Wire the form and render results into the template's IDs
let roomOptionsObj = {};
document.getElementById('planner-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const submitBtn = document.getElementById('submit-btn');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = '⏳ Analyzing...';
    submitBtn.disabled = true;

    // Read form values from template
    const data = {
        built_up_area: Number(document.getElementById('area').value) || 100,
        floors: Number(document.getElementById('floors').value) || 1,
        target_timeline: Number(document.getElementById('timeline').value) || undefined
    };
    if (roomOptionsObj && Object.keys(roomOptionsObj).length) data.room_options = roomOptionsObj;

    // show loading
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');

    try {
        const res = await fetch('/api/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        if (!res.ok) throw new Error(result.error || 'Calculation failed');

        renderResults(result, data);
        document.getElementById('results').classList.remove('hidden');
        document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
    } catch (err) {
        alert('Error: ' + err.message);
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
        document.getElementById('loading').classList.add('hidden');
    }
});

function renderResults(result, input) {
    // AI Insights (structured)
    const aiBox = document.getElementById('ai-insights');
    const aiSummary = document.getElementById('ai-summary');
    const aiToggle = document.getElementById('ai-toggle');
    aiBox.innerHTML = '';
    aiSummary.innerText = '';
    // Default collapsed
    aiBox.classList.remove('expanded');
    aiBox.classList.add('collapsed');
    aiToggle.innerText = 'Show details';

    // helper: remove markdown headings/bold and extra whitespace
    function sanitize(text) {
        if (!text) return '';
        // remove markdown headings (#, ##, ###) and bold markers (**)
        let s = text.replace(/(^|\n)#+\s*/g, '\n');
        s = s.replace(/\*\*/g, '');
        // remove leading labels like "Analysis:" or "Analysis of"
        s = s.replace(/^\s*Analysis[:\-\s]*/i, '');
        s = s.replace(/^\s*Analysis of[:\-\s]*/i, '');
        // collapse multiple newlines and trim
        s = s.replace(/\n{2,}/g, '\n').trim();
        return s;
    }

    if (result.ai_insight) {
        if (result.ai_insight.ok && Array.isArray(result.ai_insight.insights)) {
            // sanitize each insight and filter out empty/heading-only items
            const cleaned = result.ai_insight.insights.map(sanitize).filter(Boolean);
            // if first cleaned item is a short heading like "Analysis...", drop it
            if (cleaned.length && /^Analysis/i.test(cleaned[0])) cleaned.shift();

            const first = cleaned[0] || '';
            aiSummary.innerText = first.length > 140 ? first.slice(0, 137) + '...' : first || 'AI recommendations available.';

            // details list (use cleaned list)
            const ul = document.createElement('ul');
            cleaned.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;
                ul.appendChild(li);
            });
            aiBox.appendChild(ul);

            if (result.ai_insight.raw && result.ai_insight.raw.includes('AI Model Offline')) {
                aiBox.classList.add('ai-offline');
                aiSummary.classList.add('ai-offline');
            } else {
                aiBox.classList.remove('ai-offline');
                aiSummary.classList.remove('ai-offline');
            }
        } else if (typeof result.ai_insight === 'string') {
            const s = sanitize(result.ai_insight);
            aiSummary.innerText = s.split('\n')[0] || s;
            aiBox.innerText = s;
        } else if (result.ai_insight.insights) {
            const cleaned = result.ai_insight.insights.map(sanitize).filter(Boolean);
            aiSummary.innerText = cleaned[0] || 'AI recommendations available.';
            aiBox.innerText = cleaned.join('\n');
        }
    } else {
        aiSummary.innerText = 'No AI insights available.';
        aiBox.innerText = '';
    }

    // Toggle behavior
    aiToggle.onclick = function() {
        const expanded = aiBox.classList.contains('expanded');
        if (expanded) {
            aiBox.classList.remove('expanded');
            aiBox.classList.add('collapsed');
            aiToggle.innerText = 'Show details';
        } else {
            aiBox.classList.remove('collapsed');
            aiBox.classList.add('expanded');
            aiToggle.innerText = 'Hide details';
        }
    };

    // Costs
    const costEl = document.getElementById('cost-details');
    if (result.costs) {
        const c = result.costs;
        costEl.innerHTML = `
            <div><strong>Material:</strong> ₹${numberWithCommas(Math.round(c.material_cost))}</div>
            <div><strong>Labor:</strong> ₹${numberWithCommas(Math.round(c.labor_cost))}</div>
            <div><strong>Overhead:</strong> ₹${numberWithCommas(Math.round(c.overhead))}</div>
            <div style="margin-top:8px; border-top:1px solid #ddd; padding-top:8px;"><strong>Total:</strong> ₹${numberWithCommas(Math.round(c.total_cost))}</div>
        `;
    }

    // Labor
    const laborEl = document.getElementById('labor-details');
    if (result.workers) {
        let html = '';
        for (const [k, v] of Object.entries(result.workers)) {
            html += `<div><strong>${k.replace('_',' ').toUpperCase()}:</strong> ${v}</div>`;
        }
        html += `<div style="margin-top:8px;"><strong>TOTAL WORKERS:</strong> ${result.total_workers}</div>`;
        laborEl.innerHTML = html;
    }

    // Materials
    const matEl = document.getElementById('material-details');
    if (result.materials) {
        let html = '';
        for (const [k, v] of Object.entries(result.materials)) {
            html += `<div><strong>${k.toUpperCase()}:</strong> ${v}</div>`;
        }
        matEl.innerHTML = html;
    }

    // Blueprint (render SVG floor plans)
    const bpEl = document.getElementById('blueprint-details');
    bpEl.innerHTML = '';
    if (result.blueprint && Array.isArray(result.blueprint)) {
        result.blueprint.forEach(f => {
            const container = document.createElement('div');
            container.className = 'floor';
            const title = document.createElement('h4');
            title.textContent = f.floor;
            container.appendChild(title);

            // export SVG button
            const exportBtn = document.createElement('button');
            exportBtn.type = 'button';
            exportBtn.textContent = 'Export SVG';
            exportBtn.style.marginBottom = '6px';
            exportBtn.className = 'btn';
            container.appendChild(exportBtn);

            const svgNS = 'http://www.w3.org/2000/svg';
            const canvasW = (f.canvas && f.canvas.w) ? f.canvas.w : 760;
            const canvasH = (f.canvas && f.canvas.h) ? f.canvas.h : 300;
            const svg = document.createElementNS(svgNS, 'svg');
            svg.setAttribute('width', canvasW);
            svg.setAttribute('height', canvasH);
            svg.setAttribute('viewBox', `0 0 ${canvasW} ${canvasH}`);
            svg.style.border = '1px solid #e2e8f0';
            svg.style.borderRadius = '8px';
            svg.style.background = '#fff';

            // draw rooms
            if (Array.isArray(f.rooms)) {
                f.rooms.forEach((r, idx) => {
                    const rect = document.createElementNS(svgNS, 'rect');
                    rect.setAttribute('x', r.x);
                    rect.setAttribute('y', r.y);
                    rect.setAttribute('width', r.w);
                    rect.setAttribute('height', r.h);
                    rect.setAttribute('fill', '#f8fafc');
                    rect.setAttribute('stroke', '#94a3b8');
                    rect.setAttribute('stroke-width', '1');
                    svg.appendChild(rect);

                    // room label
                    const text = document.createElementNS(svgNS, 'text');
                    text.setAttribute('x', r.x + Math.max(6, r.w / 10));
                    text.setAttribute('y', r.y + 20);
                    text.setAttribute('font-size', '12');
                    text.setAttribute('fill', '#0f172a');
                    text.textContent = r.name;
                    svg.appendChild(text);

                    // dims smaller text
                    const dims = document.createElementNS(svgNS, 'text');
                    dims.setAttribute('x', r.x + Math.max(6, r.w / 10));
                    dims.setAttribute('y', r.y + 36);
                    dims.setAttribute('font-size', '11');
                    dims.setAttribute('fill', '#475569');
                    dims.textContent = r.dims;
                    svg.appendChild(dims);

                    // draw doors if present (array)
                    if (Array.isArray(r.doors)) {
                        r.doors.forEach(function(d) {
                            const door = document.createElementNS(svgNS, 'rect');
                            door.setAttribute('x', d.x);
                            door.setAttribute('y', d.y);
                            door.setAttribute('width', d.w);
                            door.setAttribute('height', d.h);
                            door.setAttribute('fill', '#8b5a2b');
                            door.setAttribute('stroke', '#5a3820');
                            door.setAttribute('stroke-width', '1');
                            svg.appendChild(door);

                            // label
                            const dl = document.createElementNS(svgNS, 'text');
                            dl.setAttribute('x', d.x + Math.max(6, d.w / 2));
                            dl.setAttribute('y', d.y + Math.max(6, d.h / 2));
                            dl.setAttribute('font-size', '10');
                            dl.setAttribute('fill', '#fff');
                            dl.setAttribute('text-anchor', 'middle');
                            dl.setAttribute('dominant-baseline', 'middle');
                            dl.textContent = 'D';
                            svg.appendChild(dl);
                        });
                    }

                    // draw windows if present
                    if (Array.isArray(r.windows)) {
                        r.windows.forEach(function(win) {
                            const wRect = document.createElementNS(svgNS, 'rect');
                            wRect.setAttribute('x', win.x);
                            wRect.setAttribute('y', win.y);
                            wRect.setAttribute('width', win.w);
                            wRect.setAttribute('height', win.h);
                            wRect.setAttribute('fill', '#e0f2ff');
                            wRect.setAttribute('stroke', '#60a5fa');
                            wRect.setAttribute('stroke-width', '1');
                            svg.appendChild(wRect);

                            // label
                            const wl = document.createElementNS(svgNS, 'text');
                            wl.setAttribute('x', win.x + Math.max(6, win.w / 2));
                            wl.setAttribute('y', win.y + Math.max(6, win.h / 2));
                            wl.setAttribute('font-size', '10');
                            wl.setAttribute('fill', '#0369a1');
                            wl.setAttribute('text-anchor', 'middle');
                            wl.setAttribute('dominant-baseline', 'middle');
                            wl.textContent = 'W';
                            svg.appendChild(wl);
                        });
                    }
                });
            }

            container.appendChild(svg);
            // wire export action after svg is appended
            exportBtn.onclick = function() {
                try {
                    const serializer = new XMLSerializer();
                    const svgString = serializer.serializeToString(svg);
                    const blob = new Blob([svgString], {type: 'image/svg+xml'});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `${f.floor.replace(/\s+/g, '_')}.svg`;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    URL.revokeObjectURL(url);
                } catch (err) {
                    alert('Failed to export SVG: ' + err.message);
                }
            };
            bpEl.appendChild(container);
        });
    }

    // Schedule
    const scheduleEl = document.getElementById('ai-schedule');
    scheduleEl.innerHTML = '';
    if (Array.isArray(result.schedule)) {
        result.schedule.forEach(w => {
            const wk = document.createElement('div');
            wk.className = 'week';
            wk.innerHTML = `<div class="week-title">Week ${w.week || ''} - ${w.phase}</div>`;
            if (Array.isArray(w.activities) && w.activities.length) {
                const acts = document.createElement('div');
                acts.className = 'activities';
                acts.textContent = w.activities.join(' · ');
                wk.appendChild(acts);
            }
            scheduleEl.appendChild(wk);
        });
    } else if (typeof result.schedule === 'string') {
        scheduleEl.innerText = result.schedule;
    }

    // Assumptions
    const assumptionsEl = document.getElementById('assumptions');
    if (assumptionsEl && result.assumptions) {
        assumptionsEl.innerHTML = `
            <div><strong>Location:</strong> ${result.assumptions.location}</div>
            <div><strong>Rate:</strong> ₹${result.assumptions.cost_per_sq_yard}/sq yard</div>
        `;
    }
}

// Room builder functionality (store options in-memory)
document.getElementById('rb-add')?.addEventListener('click', function() {
    try {
        const roomKey = document.getElementById('rb-room-type').value.trim().toLowerCase();
        const windows = parseInt(document.getElementById('rb-windows').value) || 0;
        const doors = parseInt(document.getElementById('rb-doors').value) || 0;
        const door_side = document.getElementById('rb-door-side').value;

        roomOptionsObj[roomKey] = {windows: windows, doors: doors, door_side: door_side};
        // small feedback: log to console (keeps UI minimal)
        console.log('Room option added:', roomKey, roomOptionsObj[roomKey]);
    } catch (e) {
        alert('Failed to add room option: ' + e.message);
    }
});

document.getElementById('rb-clear')?.addEventListener('click', function() {
    roomOptionsObj = {};
    console.log('Room options cleared');
});

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}
