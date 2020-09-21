$(function () {
    console.log(return_first);
    $("#moviename").autocomplete({
        source: return_first
    });
});