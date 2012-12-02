$(".keyboard-btn").click(function() {
    enterValue($(this).val());
});

function enterValue(x) {
    var input = document.getElementById("pin-input");
    input.value += x;
}

function clearPin() {
    document.getElementById("pin-input").value = '';
}

