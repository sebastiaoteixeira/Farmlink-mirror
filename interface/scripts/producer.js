var id;

function getProducerData() {
    $.post(
        "/personalData",
        {},
        (result) => {
            id = result?.id
            getProducts()
        }
    )
}

// TODO: Product list ui
function getProducts(result) {
    $.get(
        "/get/products",
        {},
        (result) => {
        }
    )
}

function addNewProduct() {
    productData = {
        name: $('#inputproductName').val(),
        type: $('#inputproductType').val(),
        price: $('#inputproductPrice').val(),
        img: $('#inputImageURL').val(),
        stock: -1,
        visible: true,
        producerId: id
    }
    $.ajax({
        url: '/addNewProduct',
        data: productData,
        type: "POST",
        enctype: 'json',
        success: function (data) {
            $('#exampleModal').modal('hide');
        }
    });
}

$(document).ready(function () {
    getProducerData()

    $(document).on('click', '#addProductSubmit', function () {
        if (!$('#inputproductName').val() || !$('#inputproductType').val() ||
            !$('#inputImageURL').val() || !$('#inputproductPrice').val()) {
            $('#addProductError').text('Please fill in all the required fields');
            return;
        } else {
            $('#addProductError').text('');
            addNewProduct()
        }
    });

    $(document).on('click', '#addProduct', function () {
        $('#exampleModalLabel').text('Add new product');
    });

    $(document).on('click', '#editProduct', function () {
        $('#exampleModalLabel').text('Edit existing product');
        $('#inputproductName').val();
        $('#inputproductType').val();
        $('#inputproductPrice').val();
        $('#inputImageURL').val();
    });


})