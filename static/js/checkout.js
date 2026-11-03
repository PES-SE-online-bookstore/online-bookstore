(function () {
    "use strict";

    const checkbox = document.getElementById("use_new_address");
    const addressFields = document.getElementById("new-address-fields");
    const savedAddressRadios = document.querySelectorAll(
        'input[name="address_id"]'
    );

    if (!checkbox || !addressFields) {
        return;
    }

    function updateAddressSelection() {
        addressFields.hidden = !checkbox.checked;

        savedAddressRadios.forEach(function (radio) {
            radio.disabled = checkbox.checked;
        });

        addressFields.querySelectorAll("input, select, textarea").forEach(
            function (field) {
                if (field.name !== "address_line_2" &&
                    field.name !== "is_default") {
                    field.required = checkbox.checked;
                }
            }
        );
    }

    checkbox.addEventListener("change", updateAddressSelection);
    updateAddressSelection();
})();
