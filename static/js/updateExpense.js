document.addEventListener('DOMContentLoaded', () => {
    const editButtons = document.querySelectorAll('.edit-button');
    
    editButtons.forEach(button => {
        button.addEventListener('click', function () {
            const expenseId = this.getAttribute('data-id');
            const description = this.getAttribute('data-description');
            const amount = this.getAttribute('data-amount');

            document.getElementById('editExpenseId').value = expenseId;
            document.getElementById('editDescription').value = description;
            document.getElementById('editAmount').value = amount;

            document.getElementById('editModal').classList.add('is-active');
        });
    });

    document.querySelectorAll('.modal-close, .modal-background').forEach(element => {
        element.addEventListener('click', () => {
            document.getElementById('editModal').classList.remove('is-active');
        });
    });
});
