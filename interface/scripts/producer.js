var id;
var productId;
var list;

function getProducerData() {
    $.post(
        "/personalData",
        {},
        (result) => {
            id = result?.producerId
            getProducts()
        }
    )
}

function getProducts(result) {
    $.get(
        "/get/products?producerId=" + id,
        {},
        (result) => {
            list = result;
            $('#productList').html('');
            for (var i = 0; i < result.length; i++) {
                let elem = $('<div></div>').addClass('row border-2').attr('itemId', result[i]?.id);
                let innerElem = $('<div></div>').addClass('col-12 rounded-2').attr('id', 'innerElem');
                let img = $('<img/>').attr('src', result[i]?.img).attr('class', 'img');
                let itemData = $('<div></div>').attr('id', "itemData");
                let itemButton = $('<button></button>').addClass('btn text-white fs-2').attr('id', "editProduct")
                    .attr('itemId', result[i]?.id)
                    .attr("data-bs-toggle", "modal").attr("data-bs-target", "#exampleModal");
                let itemButtonIcon = $('<i></i>').addClass('fa fa-edit').attr('aria-hidden', 'true');

                let itemDataName = $('<div></div>').addClass('fs-1').attr('id', "productName").text(result[i]?.name);
                let itemDataType = $('<div></div>').addClass('fs-3').attr('id', "productType").text(result[i]?.type);
                let itemDataPrice = $('<div></div>').addClass('fs-5').attr('id', "productPrice").text(result[i]?.price);
                itemData.append(itemDataName, itemDataType, itemDataPrice)
                itemButton.append(itemButtonIcon)

                $('#productList').append(elem.append(innerElem.append(img, itemData, itemButton)));
            }
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
    }
    $.ajax({
        url: '/addNewProduct',
        data: productData,
        type: "POST",
        enctype: 'json',
        success: function (data) {
            getProducts();
            $('#exampleModal').modal('hide');
            $('#inputproductName').val('');
            $('#inputproductType').val('');
            $('#inputproductPrice').val('');
            $('#inputImageURL').val('');
        }
    });
}

function editProduct() {
    productData = {
        name: $('#inputproductName').val(),
        type: $('#inputproductType').val(),
        price: $('#inputproductPrice').val(),
        img: $('#inputImageURL').val(),
        productId: productId
    }
    $.ajax({
        url: '/editProduct',
        data: productData,
        type: "POST",
        enctype: 'json',
        success: function (data) {
            getProducts();
            $('#exampleModal').modal('hide');
            $('#inputproductName').val('');
            $('#inputproductType').val('');
            $('#inputproductPrice').val('');
            $('#inputImageURL').val('');
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

    $(document).on('click', '#editProductSubmit', function () {
        if (!$('#inputproductName').val() || !$('#inputproductType').val() ||
            !$('#inputImageURL').val() || !$('#inputproductPrice').val()) {
            $('#addProductError').text('Please fill in all the required fields');
            return;
        } else {
            $('#addProductError').text('');
            editProduct()
        }
    });


    $(document).on('click', '#addProduct', function () {
        $('#exampleModalLabel').text('Add new product');
         $("#addProductSubmit").removeClass('display_none');
        $("#editProductSubmit").addClass('display_none');
    });

    $(document).on('click', '#editProduct', function () {
        $("#addProductSubmit").addClass('display_none');
        $("#editProductSubmit").removeClass('display_none');
        productId = $(this).attr('itemId')
        $('#exampleModalLabel').text('Edit existing product');

        for (var i = 0; i < list.length; i++) {
            if (list[i]?.id == productId) {
                $('#inputproductName').val(list[i]?.name);
                $('#inputproductType').val(list[i]?.type);
                $('#inputproductPrice').val(list[i]?.price);
                $('#inputImageURL').val(list[i]?.img);
            }
        };

    });


})