document.getElementById('planner-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const area = document.getElementById('area').value;
    const floors = document.getElementById('floors').value;
    const timeline = document.getElementById('timeline').value;
    
    const resultsSection = document.getElementById('results');
    const loadingSection = document.getElementById('loading');
    const submitBtn = document.getElementById('submit-btn');
    
    // UI state
    submitBtn.disabled = true;
    loadingSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    
    try {
        const response = await fetch('/api/plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ area, floors, timeline })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data);
            resultsSection.classList.remove('hidden');
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to connect to the server.');
    } finally {
        submitBtn.disabled = false;
        loadingSection.classList.add('hidden');
    }
});

function displayResults(data) {
    // Costs
    const costDiv = document.getElementById('cost-details');
    costDiv.innerHTML = `
        <p><span>Material Cost:</span> <strong>₹${data.costs.material_cost.toLocaleString()}</strong></p>
        <p><span>Labor Cost:</span> <strong>₹${data.costs.labor_cost.toLocaleString()}</strong></p>
        <p><span>Overhead (10%):</span> <strong>₹${data.costs.overhead.toLocaleString()}</strong></p>
        <p><span>Total Project Cost:</span> <strong>₹${data.costs.total_cost.toLocaleString()}</strong></p>
        <p><span>Cost per Sq Yard:</span> <strong>₹${data.costs.cost_per_sq_yard.toLocaleString()}</strong></p>
    `;
    
    // Labor
    const laborDiv = document.getElementById('labor-details');
    laborDiv.innerHTML = `
        <p><span>Estimated Timeline:</span> <strong>${data.labor.estimated_days} days</strong></p>
        <p><span>Masons:</span> <strong>${data.labor.masons}</strong></p>
        <p><span>Helpers:</span> <strong>${data.labor.helpers}</strong></p>
        <p><span>Steel Workers:</span> <strong>${data.labor.steel_workers}</strong></p>
        <p><span>Carpenters:</span> <strong>${data.labor.carpenters}</strong></p>
        <p><span>Supervisors:</span> <strong>${data.labor.supervisors}</strong></p>
    `;
    
    // Materials
    const materialDiv = document.getElementById('material-details');
    materialDiv.innerHTML = `
        <p><span>Cement:</span> <strong>${data.materials.cement} bags</strong></p>
        <p><span>Steel:</span> <strong>${data.materials.steel} kg</strong></p>
        <p><span>Sand:</span> <strong>${data.materials.sand} cu ft</strong></p>
        <p><span>Aggregate:</span> <strong>${data.materials.aggregate} cu ft</strong></p>
        <p><span>Bricks:</span> <strong>${data.materials.bricks.toLocaleString()} pcs</strong></p>
    `;
    
    // Blueprint
    const bpDiv = document.getElementById('blueprint-details');
    let roomsHtml = '<ul>';
    for (const [room, size] of Object.entries(data.blueprint.suggested_rooms)) {
        roomsHtml += `<li><strong>${room}:</strong> ${size}</li>`;
    }
    roomsHtml += '</ul>';
    bpDiv.innerHTML = `
        <p><strong>Total Area:</strong> ${data.blueprint.total_area}</p>
        <p><strong>Room Breakdown:</strong></p>
        ${roomsHtml}
        <p><small>${data.blueprint.notes}</small></p>
    `;
    
    // AI Insights
    document.getElementById('ai-insights').innerText = data.ai_insights;
    
    // AI Schedule
    document.getElementById('ai-schedule').innerText = data.ai_schedule;
}
