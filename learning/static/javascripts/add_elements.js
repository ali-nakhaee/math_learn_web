var i = 0;

function addMore()
{
var x = document.getElementById('add_answer');
var input1 = document.createElement("input");
input1.setAttribute("type","text");
input1.setAttribute("name","i" + i );
x.appendChild( input1 );
i++;
}
