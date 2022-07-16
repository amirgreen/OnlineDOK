var inputs = document.querySelectorAll( '.inputfile' );
Array.prototype.forEach.call( inputs, function( input )
{
	var label	 = input.nextElementSibling,
		labelVal = label.innerHTML;

	input.addEventListener( 'change', function( e )
	{
		var fileName = '';
		if( this.files && this.files.length > 1 )
			fileName = ( this.getAttribute( 'data-multiple-caption' ) || '' ).replace( '{count}', this.files.length );
		else
			fileName = e.target.value.split( '\\' ).pop();

		if( fileName )
			label.querySelector( 'span' ).innerHTML = fileName;
		else
			label.innerHTML = labelVal;
	});
});


function CheckValid(form) {
    if (document.getElementById("password1").value != document.getElementById("password2").value) {
        document.getElementById("password2").setCustomValidity("Please Match The passwords");
        form.password2.focus();
        return false;
    }
    
    return true;
}

function inputStyle() {
    if (document.getElementById("password1").value != document.getElementById("password2").value || document.getElementById("password2").value == "") {
        document.getElementById("password2").className = "invalid";
    }
    else {
        document.getElementById("password2").className = "valid";
    }
}

var prompt = true;
function show(id) {
    prompt = !prompt;
    if (prompt) {
        id.style.visibility = "hidden";
        id.style.opacity = 0;
    }
    else {
        id.style.visibility = "visible";
        id.style.opacity = 1;
    }
}

function EnableCheckbox() {
    document.getElementById("<%=chkMyCheckbox.clientID  %>").disabled = false;
}

var slideIndex = 1
function plusDivs(n, className) {
    showDivs(slideIndex += n, className);
}

function showDivs(n, className) {
    var i;
    var x = document.getElementsByClassName(className);
    if (n > x.length) { slideIndex = 1 }
    if (n < 1) { slideIndex = x.length };
    for (i = 0; i < x.length; i++) {
        x[i].style.display = "none";
    }
    x[slideIndex - 1].style.display = "block";
}

function closeAlert(btn) {
        // Get the parent of <span class="closebtn"> (<div class="alert">)
        var div = btn.parentElement;

        // Set the opacity of div to 0 (transparent)
        div.style.opacity = "0";

        // Hide the div after 600ms (the same amount of milliseconds it takes to fade out)
        setTimeout(function(){ div.style.display = "none"; }, 600);
}

function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
    document.getElementById("main").style.marginLeft = "250px";
}

/* Set the width of the side navigation to 0 and the left margin of the page content to 0 */
function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
    document.getElementById("main").style.marginLeft = "0";
}

function changeNav() {
    if (document.getElementById("mySidenav").style.width == "250px") {
        closeNav()
    }
    else {
        openNav()
    }
}


function toggleSideNav(dropdown){
    dropdown.classList.toggle("active");
    var dropdownContent = dropdown.nextElementSibling;
    if (dropdownContent.style.display === "block") {
      dropdownContent.style.display = "none";
    } else {
      dropdownContent.style.display = "block";
    }
}