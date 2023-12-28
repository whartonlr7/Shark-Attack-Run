function filteredByDate() {
    const filteredByDate = document.querySelector('#dateFilter').checked
    const elements = document.querySelectorAll('.visibleIfDateFilter');
    elements.forEach(element => {
        element.required = filteredByDate
        element.style.display = filteredByDate ? 'inline' : 'none'
    });
}

function confirmValidForm() {
    const startDate = document.querySelector('#startDate');
    const endDate = document.querySelector('#endDate');
    if(startDate.value.localeCompare(endDate.value) > 0 && startDate.style.display !== 'none') {
        alert('Please ensure that your end date is not before your start date')
        return false;
    }
    return true;
}