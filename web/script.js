$(function(){
	$("#nav li a").each(function(){
		var page = $(this).attr("data-page");
		if (typeof page !== typeof undefined && page !== false)
			$("#content").append($('<div />', { "class": 'padded page', "id": "page-" + page.split("/")[1] }).load("web/pages/" + page + ".html"))
	});
	
	$("#nav li a").click(function(){
		var page = $(this).attr("data-page");
		if (typeof page !== typeof undefined && page !== false)
		{
			$(".page").hide();
			$("#page-" + page.split("/")[1]).show()
		}
	});
	
	
	$(".page").hide();
})