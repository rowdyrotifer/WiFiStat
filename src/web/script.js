$(function(){
	//Load each of the pages from the data-page attributes of the navigation elements.
	$("#nav li a").each(function(){
		var page = $(this).attr("data-page");
		if (typeof page !== typeof undefined && page !== false)
			$("#content").append($('<div />', { "class": 'padded page', "id": "page-" + page.split("/")[1] }).load("src/web/pages/" + page + ".html"))
	}).promise().done(function(){
		//Hide all the just-loaded pages.
		$(".page").each(function(){
			$(this).hide(1);
		//Show the default.
		}).promise().done(function(){
			$("a[data-default='true']").click();
		});
	});
	
	//Hide others and show clicked page.
	$("#nav li a").click(function(){
		var page = $(this).attr("data-page");
		var pageobj = $("#page-" + page.split("/")[1]);
		if (typeof page !== typeof undefined && page !== false)
		{
			//Hide the visible pages.
			$(".page:visible").not(pageobj).each(function(){
				$(this).slideUp(150);
			//Show the selected page.
			}).promise().done(function(){
				pageobj.slideDown(150);
			});
		}
	});
	
	//Server shutdown :(
	$("#shutdown").click(function(){
		$.get( "./", { shutdown: "true" } ).done(function(data) {
		    response = JSON.parse(data);
		    if (response[0] == "shutdown")
		    	window.open('','_self').close();
		    else
		    	alert("The server could not be shut down...");
		  });
	})
})