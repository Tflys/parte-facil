// static/js/add_work.js
let step = 1;
function gotoStep(n) {
    for (let i = 1; i <= 3; i++) {
        document.getElementById("step-" + i).classList.remove("active");
    }
    document.getElementById("step-" + n).classList.add("active");
    // Actualizar barra de progreso
    const pct = n * 33;
    document.getElementById("progressBar").style.width = pct + "%";
    document.getElementById("progressBar").innerText = `Paso ${n} de 3`;
    step = n;
    window.scrollTo({top: 0, behavior: "smooth"});
}
function toggleMateriales() {
    let chk = document.getElementById('materialesSwitch');
    let div = document.getElementById('materialesDiv');
    div.style.display = chk.checked ? 'block' : 'none';
    if (!chk.checked) {
        document.querySelector('[name="materiales_usados"]').value = '';
    }
}
document.addEventListener("DOMContentLoaded", function() {
    gotoStep(1);
    toggleMateriales();
});
