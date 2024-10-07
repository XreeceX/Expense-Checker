document.getElementById('exportButton').addEventListener('click', function() {
    const expenseData = [
        ["Date", "Item", "Amount", "Total"],
        ["2024-10-07", "Groceries", 50, 100],
        ["2024-10-06", "Transport", 20, 80],
    ];
    const csvContent = expenseData.map(e => e.join(",")).join("\n");

    const blob = new Blob([csvContent], { type: 'text/csv' });

    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'expenses.csv';
    document.body.appendChild(link);
    link.click();

    document.body.removeChild(link);
});
