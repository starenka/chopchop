var offset = false;

$(document).ready(function() {	
	
	$('button[class!=delete]').click(function(){
		$(this).toggleClass('active');
		filter();
	});
	
	$('button.delete').click(function(){
		remove_filter(($(this).id == null)?false:$(this).id);
	});

	//$('.input').change(function(){filter();});		
	$('.input').bind('keypress',function(e){ if(e.keyCode==13) filter();});
	
	$('a.pagination').click(function(){
		offset = $(this).attr('id').split('-')[1];
		filter();
		return false;
	});
	
	$('#show-more-qry').click(function(){ $('#more-qry').toggle(); return false;});
	$('#show-more-filter').click(function(){ $('#more-filter').toggle(); return false;});
	//$('#refresh').click(function(){ window.location.reload(); return false;});
	$('#reset').click(function(){ window.location = base_url; return false;});
});

function filter()
{
	filter = '';
	$.each($('button.active'),function(i,el){
		filter += '&levels='+$(el).attr('id');
	});
	
	$.each($('.input'),function(i,el){
		filter += '&'+$(el).attr('name')+'='+$(el).attr('value');
	});
	
	filter += '&offset='+offset;
	
	window.location = base_url+'?'+filter;
}

function remove_filter(filter)
{
	if (filter == false) 
		window.location = base_url;
	else {
		loc = window.location.toString();
		loc = loc.replace('(&'+filter+'=.*?)','');
	}
}