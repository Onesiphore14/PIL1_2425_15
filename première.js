
function gererOptions() {
    const OptionA =
        document.getElementById('OptionA');
    const OptionB =
        document.getElementById('OptionB');
    if (OptionA.checked) { OptionB.disabled = true; }
    else if (OptionB.checked) { OptionA.disabled = true; }
    else { OptionA.disabled = false; OptionB.disabled = false; }
}
