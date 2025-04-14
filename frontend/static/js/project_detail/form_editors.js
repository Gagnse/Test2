/**
 * Handles form editing functionality for the project detail page's special tabs
 */
document.addEventListener("DOMContentLoaded", function () {
    // Functionality tab edit button
    const functionalityEditIcon = document.querySelector("#tab-functionality .edit-icon");
    if (functionalityEditIcon) {
        functionalityEditIcon.addEventListener("click", function () {
            const form = document.querySelector("#tab-functionality .functionality-form[style*='block']");
            if (!form) return;

            form.querySelectorAll("input, textarea").forEach(el => el.removeAttribute("disabled"));

            if (!form.querySelector(".save-button")) {
                const btn = document.createElement("button");
                btn.className = "save-button";
                btn.textContent = "Enregistrer";
                btn.style.marginTop = "10px";
                form.appendChild(btn);

                btn.addEventListener("click", function (e) {
                    e.preventDefault();
                    const roomId = form.dataset.roomId;
                    const data = {
                        room_id: roomId,
                        functionality_occupants_number: form.querySelector("#occupants").value,
                        functionality_desk_number: form.querySelector("#desk").value,
                        functionality_lab_number: form.querySelector("#lab").value,
                        functionality_schedule: form.querySelector("#schedule").value,
                        functionality_description: form.querySelector("#description").value,
                        functionality_proximity: form.querySelector("#proximity").value,
                        functionality_commentary: form.querySelector("#commentary").value,
                        functionality_access: [],
                        functionality_consideration: []
                    };

                    form.querySelectorAll("input[name='functionality_access']:checked").forEach(cb => {
                        data.functionality_access.push(cb.value);
                    });

                    form.querySelectorAll("input[name='functionality_consideration']:checked").forEach(cb => {
                        data.functionality_consideration.push(cb.value);
                    });

                    fetch(`/workspace/projects/{{ project.id }}/edit_functionality`, {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify(data)
                    })
                        .then(r => r.json())
                        .then(res => {
                            if (res.success) {
                                alert("Modifications enregistrées !");
                                form.querySelectorAll("input, textarea").forEach(el => el.setAttribute("disabled", "true"));
                            } else {
                                alert("Erreur : " + res.message);
                            }
                        })
                        .catch(err => console.error("Erreur :", err));
                });
            }
        });
    }

    // Architectural requirements tab edit button
    const archEditIcon = document.querySelector("#tab-arch_requirements .edit-icon");
    if (archEditIcon) {
        archEditIcon.addEventListener("click", function () {
            const form = document.querySelector("#tab-arch_requirements .arch_requirements-form[style*='block']");
            if (!form) return;

            form.querySelectorAll("input, textarea").forEach(el => el.removeAttribute("disabled"));

            if (!form.querySelector(".save-button")) {
                const btn = document.createElement("button");
                btn.className = "save-button";
                btn.textContent = "Enregistrer";
                btn.style.marginTop = "10px";
                form.appendChild(btn);

                btn.addEventListener("click", function (e) {
                    e.preventDefault();
                    const data = {
                        room_id: form.dataset.roomId,
                        arch_requirements_critic_length: form.querySelector("#arch_requirements_critic_length").value,
                        arch_requirements_critic_width: form.querySelector("#arch_requirements_critic_width").value,
                        arch_requirements_critic_height: form.querySelector("#arch_requirements_critic_height").value,
                        arch_requirements_validation_req: form.querySelector("#arch_requirements_validation_req").value,
                        arch_requirements_acoustic: form.querySelector("#arch_requirements_acoustic").value,
                        arch_requirements_int_fenestration: [],
                        arch_requirements_int_fen_adj_room: form.querySelector("#arch_requirements_int_fen_adj_room").value,
                        arch_requirements_int_fen_other: form.querySelector("#arch_requirements_int_fen_other").value,
                        arch_requirements_ext_fenestration: [],
                        arch_requirements_ext_fen_solar_blind: form.querySelector("#arch_requirements_ext_fen_solar_blind").value,
                        arch_requirements_ext_fen_opaque_blind: form.querySelector("#arch_requirements_ext_fen_opaque_blind").value,
                        arch_requirements_commentary: form.querySelector("#arch_requirements_commentary").value
                    };

                    // Collect checkboxes
                    form.querySelectorAll("input[name='arch_requirements_int_fenestration']:checked").forEach(cb => {
                        data.arch_requirements_int_fenestration.push(cb.value);
                    });
                    form.querySelectorAll("input[name='arch_requirements_ext_fenestration']:checked").forEach(cb => {
                        data.arch_requirements_ext_fenestration.push(cb.value);
                    });

                    fetch(`/workspace/projects/{{ project.id }}/edit_arch_requirements`, {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify(data)
                    })
                        .then(r => r.json())
                        .then(res => {
                            if (res.success) {
                                alert("Modifications enregistrées !");
                                form.querySelectorAll("input, textarea").forEach(el => el.setAttribute("disabled", "true"));
                            } else {
                                alert("Erreur : " + res.message);
                            }
                        })
                        .catch(err => console.error("Erreur :", err));
                });
            }
        });
    }

    // Structural requirements tab edit button
    const structEditIcon = document.querySelector("#tab-struct_requirements .edit-icon");
    if (structEditIcon) {
        structEditIcon.addEventListener("click", function () {
            const form = document.querySelector("#tab-struct_requirements .struct-form[style*='block']");
            if (!form) return;

            form.querySelectorAll("input, textarea").forEach(el => el.removeAttribute("disabled"));

            if (!form.querySelector(".save-button")) {
                const btn = document.createElement("button");
                btn.className = "save-button";
                btn.textContent = "Enregistrer";
                btn.style.marginTop = "10px";
                form.appendChild(btn);

                btn.addEventListener("click", function (e) {
                    e.preventDefault();
                    const data = {
                        room_id: form.dataset.roomId,
                        struct_requirements_floor_overload_required: form.querySelector("#struct_overload_req").checked ? 1 : 0,
                        struct_requirements_overload: form.querySelector("#struct_overload").value || null,
                        struct_requirements_equipment_weight: form.querySelector("#struct_equip_weight").value || null,
                        struct_requirements_floor_flatness: form.querySelector("#struct_flatness").checked ? 1 : 0,
                        struct_requirements_ditch_gutter: form.querySelector("#struct_ditch").checked ? 1 : 0,
                        struct_requirements_steel_sensitivity: form.querySelector("#struct_steel").checked ? 1 : 0,
                        struct_requirements_equipment_other: form.querySelector("#struct_equipment_other").value,
                        struct_requirements_vibrations_sensitivity: form.querySelector("#struct_vibration").checked ? 1 : 0,
                        struct_requirements_max_vibrations: form.querySelector("#struct_vibration_max").value || null,
                        struct_requirements_commentary: form.querySelector("#struct_commentary").value
                    };


                    fetch(`/workspace/projects/{{ project.id }}/edit_struct_requirements`, {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify(data)
                    })
                        .then(r => r.json())
                        .then(res => {
                            if (res.success) {
                                alert("Modifications enregistrées !");
                                form.querySelectorAll("input, textarea").forEach(el => el.setAttribute("disabled", "true"));
                            } else {
                                alert("Erreur : " + res.message);
                            }
                        })
                        .catch(err => console.error("Erreur :", err));
                });
            }
        });
    }

    // Risk elements tab edit button
    const riskEditIcon = document.querySelector("#tab-risk_elements .edit-icon");
    if (riskEditIcon) {
        riskEditIcon.addEventListener("click", function () {
            const form = document.querySelector("#tab-risk_elements .risk-form[style*='block']");
            if (!form) return;

            form.querySelectorAll("input, textarea").forEach(el => el.removeAttribute("disabled"));

            if (!form.querySelector(".save-button")) {
                const btn = document.createElement("button");
                btn.className = "save-button";
                btn.textContent = "Enregistrer";
                btn.style.marginTop = "10px";
                form.appendChild(btn);

                btn.addEventListener("click", function (e) {
                    e.preventDefault();
                    const roomId = form.dataset.roomId;
                    const data = {
                        room_id: roomId,
                        risk_elements_general: [],
                        risk_elements_biological: [],
                        risk_elements_gas: [],
                        risk_elements_liquids: [],
                        risk_elements_other: [],
                        risk_elements_general_radioactive: form.querySelector("#risk_elements_general_radioactive").value,
                        risk_elements_gas_qty: form.querySelector("#risk_elements_gas_qty").value,
                        risk_elements_gas_toxic_gas: form.querySelector("#risk_elements_gas_toxic_gas").value,
                        risk_elements_liquids_qty: form.querySelector("#risk_elements_liquids_qty").value,
                        risk_elements_liquids_cryogenic: form.querySelector("#risk_elements_liquids_cryogenic").value,
                        risk_elements_chemical_products: form.querySelector("#risk_elements_chemical_products").value,
                        risk_elements_commentary: form.querySelector("#risk_elements_commentary").value
                    };

                    form.querySelectorAll("input[name='risk_elements_general']:checked").forEach(cb => data.risk_elements_general.push(cb.value));
                    form.querySelectorAll("input[name='risk_elements_biological']:checked").forEach(cb => data.risk_elements_biological.push(cb.value));
                    form.querySelectorAll("input[name='risk_elements_gas']:checked").forEach(cb => data.risk_elements_gas.push(cb.value));
                    form.querySelectorAll("input[name='risk_elements_liquids']:checked").forEach(cb => data.risk_elements_liquids.push(cb.value));
                    form.querySelectorAll("input[name='risk_elements_other']:checked").forEach(cb => data.risk_elements_other.push(cb.value));

                    fetch(`/workspace/projects/{{ project.id }}/edit_risk_elements`, {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify(data)
                    })
                        .then(r => r.json())
                        .then(res => {
                            if (res.success) {
                                alert("Modifications enregistrées !");
                                form.querySelectorAll("input, textarea").forEach(el => el.setAttribute("disabled", "true"));
                            } else {
                                alert("Erreur : " + res.message);
                            }
                        })
                        .catch(err => console.error("Erreur :", err));
                });
            }
        });
    }

    // Ventilation CVAC tab edit button
    const ventilationEditIcon = document.querySelector("#tab-ventilation_cvac .edit-icon");
    if (ventilationEditIcon) {
        ventilationEditIcon.addEventListener("click", function () {
            const form = document.querySelector("#tab-ventilation_cvac .ventilation-form[style*='block']");
            if (!form) return;

            form.querySelectorAll("input, textarea").forEach(el => el.removeAttribute("disabled"));

            if (!form.querySelector(".save-button")) {
                const btn = document.createElement("button");
                btn.className = "save-button";
                btn.textContent = "Enregistrer";
                btn.style.marginTop = "10px";
                form.appendChild(btn);

                btn.addEventListener("click", function (e) {
                    e.preventDefault();
                    const roomId = form.dataset.roomId;
                    const data = {
                        room_id: roomId,
                        ventilation_care_area_type: form.querySelector("#ventilation_care_area_type").value,
                        ventilation: form.querySelector("#ventilation").value,
                        ventilation_special_mechanics: form.querySelector("#ventilation_special_mechanics").value,
                        ventilation_specific_exhaust: form.querySelector("#ventilation_specific_exhaust").value,
                        ventilation_commentary: form.querySelector("#ventilation_commentary").value,
                        ventilation_relative_room_pressure: form.querySelector("#ventilation_relative_room_pressure").value,
                        ventilation_pressurization: form.querySelector("#ventilation_pressurization").value,
                        ventilation_environmental_parameters: form.querySelector("#ventilation_environmental_parameters").value
                    };

                    fetch(`/workspace/projects/{{ project.id }}/edit_ventilation_cvac`, {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify(data)
                    })
                        .then(r => r.json())
                        .then(res => {
                            if (res.success) {
                                alert("Modifications enregistrées !");
                                form.querySelectorAll("input, textarea").forEach(el => el.setAttribute("disabled", "true"));
                            } else {
                                alert("Erreur : " + res.message);
                            }
                        })
                        .catch(err => console.error("Erreur :", err));
                });
            }
        });
    }

    // Electricity tab edit button
    const electricityEditIcon = document.querySelector("#tab-electricity .edit-icon");
    if (electricityEditIcon) {
        electricityEditIcon.addEventListener("click", function () {
            const form = document.querySelector("#tab-electricity .electricity-form[style*='block']");
            if (!form) return;

            // Activate all text areas
            form.querySelectorAll("input, textarea").forEach(el => el.removeAttribute("disabled"));

            // Add buttons
            if (!form.querySelector(".save-button")) {
                const btn = document.createElement("button");
                btn.className = "save-button";
                btn.textContent = "Enregistrer";
                btn.style.marginTop = "10px";
                form.appendChild(btn);

                btn.addEventListener("click", function (e) {
                    e.preventDefault();

                    const roomId = form.dataset.roomId;
                    const data = {
                        room_id: roomId,
                        electricity_care_area_type: form.querySelector("#electricity_care_area_type").value,
                        electricity_smoke_fire_detection: form.querySelector("#electricity_smoke_fire_detection").value,
                        electricity_special_equipment: form.querySelector("#electricity_special_equipment").value,
                        electricity_lighting_type: form.querySelector("#electricity_lighting_type").value,
                        electricity_lighting_level: form.querySelector("#electricity_lighting_level").value,
                        electricity_lighting_control: form.querySelector("#electricity_lighting_control").value,
                        color_temperature: form.querySelector("#color_temperature").value,
                        electricity_lighting: form.querySelector("#electricity_lighting").value,
                        electricity_commentary: form.querySelector("#electricity_commentary").value
                    };

                    fetch(`/workspace/projects/{{ project.id }}/edit_electricity`, {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify(data)
                    })
                        .then(r => r.json())
                        .then(res => {
                            if (res.success) {
                                alert("Modifications enregistrées !");
                                form.querySelectorAll("input, textarea").forEach(el => el.setAttribute("disabled", "true"));
                            } else {
                                alert("Erreur : " + res.message);
                            }
                        })
                        .catch(err => console.error("Erreur :", err));
                });
            }
        });
    }

    // Handle Tab Activation and Persistence
    const tabButtons = document.querySelectorAll(".tab-button");

    // Save active tab
    tabButtons.forEach(button => {
        button.addEventListener("click", function () {
            const tab = this.getAttribute("data-tab");
            localStorage.setItem("activeTab", tab);
        });
    });

    // Reactivate the tab and display data
    function activateTab(tabId) {
        document.querySelectorAll(".tab-button").forEach(btn => btn.classList.remove("active"));
        document.querySelectorAll(".tab-content").forEach(tab => tab.classList.remove("active"));

        const btn = document.querySelector(`.tab-button[data-tab="${tabId}"]`);
        const content = document.querySelector(`#tab-${tabId}`);
        if (btn && content) {
            btn.classList.add("active");
            content.classList.add("active");

            // Case special tab
            const form = content.querySelector("form");
            if (form) {
                form.style.display = "block";

                // Reactivate cells
                form.querySelectorAll("input, textarea, select").forEach(el => {
                    el.setAttribute("disabled", "true");
                });

                // remove buttons
                content.querySelectorAll(".save-button, .cancel-button").forEach(btn => btn.remove());
            }
        }
    }

    // Restore active tab on load
    const savedTab = localStorage.getItem("activeTab");
    if (savedTab) {
        activateTab(savedTab);
    }
});

// Function to initialize dropdown toggles for special tabs
function initSpecialTabDropdowns() {
    // Get all dropdown toggles in special tabs
    const specialTabDropdowns = document.querySelectorAll('.special-tab-container .dropdown-toggle');

    // Add click event listeners to each toggle
    specialTabDropdowns.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            // Toggle the active class on the parent dropdown
            const dropdown = this.closest('.project-actions-dropdown');

            // First close all other dropdowns
            document.querySelectorAll('.project-actions-dropdown.active').forEach(openDropdown => {
                if (openDropdown !== dropdown) {
                    openDropdown.classList.remove('active');
                }
            });

            // Toggle this dropdown
            dropdown.classList.toggle('active');
        });
    });

    // Close all dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.project-actions-dropdown')) {
            document.querySelectorAll('.project-actions-dropdown.active').forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        }
    });
}

// Call this function when the document is loaded
document.addEventListener('DOMContentLoaded', function() {
    initSpecialTabDropdowns();
});