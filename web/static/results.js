formatTables();
let graphs = [];

function formatTables() {
    const tables = document.querySelectorAll('.table-container');
    if(tables.length !== 0) {
        positionTables(tables);
    }
    else noResults();
}

function positionTables(tables) {
    let i = 0;
    let row = 0;
    let height = tables[0].offsetHeight;
    let zIdx = -1;
    tables.forEach(table => {
        if (i === 4) {
            i = 0;
            row++;
            zIdx--;
        }
        table.style.left = i++ / 4 * 100 + '%';
        table.style.top = row * height + 'px';
        table.style.zIndex = '' + zIdx;
        table.addEventListener('click', () => tableSelected(table))
        table.querySelectorAll('td').forEach(element => {
            if(element.innerHTML === 'None') element.innerHTML = 'Unknown'
        });
    });
    let idDiv = document.querySelector('#ids');
    idDiv.style.zIndex = '' + zIdx;
    idDiv.style.height = row * height + 500 + 'px';
}

function noResults() {
    console.log('hello');
        let div = document.querySelector('#ids');
        div.appendChild(
            Object.assign(
                document.createElement('h2'), {
                    style : 'color: red;',
                    innerHTML : 'Sorry, no results matched your search.'
                }
            )
        );
        document.body.removeChild(document.querySelector('#comparer-container'));
}

function tableSelected(table) {
    if(document.querySelector('#comparer-container').classList.contains('comparing')) return;
    table.classList.toggle("selected");
    updateCompare();
}

// Called when a new button is selected, updates the bottom display by putting in new button
function updateCompare() {
    const compares = document.querySelectorAll('.selected .attack-id');
    const comparer = document.querySelector('#comparer-display')
    const container = document.querySelector('#comparer-container')
    try {
        container.removeChild(container.querySelector('button'));
    } catch(ignored) {}
    while(comparer.childNodes.length !== 0) {
        comparer.removeChild(comparer.childNodes[0]);
    }
    if (compares.length === 0) {
        comparer.classList.remove('compares-selected');
        comparer.innerHTML = 'Click on any id to add it to the comparison.';
        return;
    }
    container.insertBefore(Object.assign(document.createElement('button'), {
        id : 'compare-button',
        innerHTML: 'Compare'
    }), comparer);
    document.querySelector('button').addEventListener('click', () => compare())
    comparer.className = 'compares-selected';
    compares.forEach(id => {
        comparer.appendChild(
            Object.assign(document.createElement('button'), {
                innerHTML : id.innerHTML
            })).addEventListener('click', () => remove(id))
    });
}

// unselects clicked button
function remove(id) {
    document.querySelectorAll('.selected').forEach((table) => {
        if(table.querySelector('th').innerHTML === id.innerHTML) {
            table.classList.toggle('selected');
            updateCompare();
        }
    });
}

//makes table and hides everything else when compared
function compare() {
    const comparer = document.querySelector('#comparer-container')
    comparer.className = 'comparing';
    const quitButton = comparer.appendChild(Object.assign(document.createElement('button'), {
        innerHTML : 'x',
        id : 'quit-button'
    }));
    quitButton.addEventListener('click', () => closeCompare())
    const table = comparer.appendChild(document.createElement('table'));
    const categories = ['ID', 'Date', 'Country', 'Place', 'State', 'Injury', 'Species', 'Activity'];
    for(let i = 0; i < categories.length; i++) {
        const row = table.appendChild(document.createElement('tr'));
        row.appendChild(Object.assign(document.createElement('th'), {innerHTML : categories[i]}));
        const entries = document.querySelectorAll('.selected tr:nth-child(' + (i + 1) + ') ' + (i === 0 ? 'th' : 'td'));
        entries.forEach(entry => row.appendChild(Object.assign(document.createElement('td'), {innerHTML : entry.innerHTML})));
    }
}

// deletes table and returns appearance to before
function closeCompare() {
    const comparer = document.querySelector('#comparer-container')
    comparer.removeChild(document.querySelector('#quit-button'));
    comparer.removeChild(document.querySelector('#comparer-container table'));
    document.querySelector('#comparer-container').className = 'compares-selected';
}

function generateGraphs(data, graphTitle, canvas) {
    const graph = []
    for(let entry in data) {
        graph[graph.length] = {name: entry, count: data[entry]}
    }
    graphs[graphs.length] = new Chart(canvas.getContext('2d'), {
        type: 'bar',
        data: {
            labels: graph.map(row => row.name),
            datasets: [{
                label: 'Attacks',
                data: graph.map(row => row.count)
            }],
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: graphTitle
                }
            }
        }
    });
}

function deleteGraphs() {
    for (let id in Chart.instances) {
        Chart.instances[id].destroy();
    }
}