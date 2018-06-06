function confirmDelete (url) {
    var confirm = window.confirm("Êtes vous sûr de vouloir supprimer cet élément ?\nIl est possible qu'il soit associé à un autre élément.")
    if (confirm)
        window.location.href = url
}

$('.delete').click(function (e) {
    e.preventDefault()
    confirmDelete($(this).attr('href'))
})

$('#editBtn').click(function() {
    $('input#username').prop('disabled', false)
})

$('#editUserForm').submit(function(e) {
    $('input#username').prop('disabled', false)

})
