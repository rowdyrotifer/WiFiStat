$(function(){
	//Load each of the pages.
	$("#nav li a").each(function(){
		var page = $(this).attr("data-page");
		if (typeof page !== typeof undefined && page !== false)
			$("#content").append($('<div />', { "class": 'padded page', "id": "page-" + page.split("/")[1] }).load("src/web/pages/" + page + ".html"))
	});
	
	//Hide all and then show the default.
	$(".page").hide(function(){$("a[data-default='true']").click();});
	
	$("#nav li a").click(function(){
		var page = $(this).attr("data-page");
		if (typeof page !== typeof undefined && page !== false)
		{
			$(".page").hide();
			$("#page-" + page.split("/")[1]).show()
		}
	});
	
	$("#shutdown").click(function(){
		$.get( "./", { shutdown: "true" } ).done(function( data ) {
		    response = JSON.parse(data);
		    if (response[0] == "shutdown")
	    	{
		    	//location.reload();
		    	window.open('','_self').close();
	    	}
		    else
		    	alert("The server could not be shut down...");
		  });
	})
})