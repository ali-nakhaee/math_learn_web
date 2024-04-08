var step = 1;

function addField(type) {
    var practice_form = document.getElementById('practice_form');
    var input = document.createElement("input");
    input.setAttribute("type", "text");
    
    if (type == 'text') {
        input.setAttribute("name", "text_" + step);
    } else if (type == 'answer') {
        input.setAttribute("name", "answer_" + step);
    } else if (type == 'help') {
        input.setAttribute("name", "help_" + step);
    }

    practice_form.appendChild(input);
    step++;
}
