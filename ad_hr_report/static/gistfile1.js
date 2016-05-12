// Examples can be found here: http://boedesign.com/misc/outer_setters.html
// Discussed here: http://forum.jquery.com/topic/outerheight-int-sets-the-height-taking-into-account-padding-and-border

(function($){
	
	function _outerSetter(direction, args){

		var $el = $(this),
			$sec_el = $(args[0]),
			dir = (direction == 'Height') ? ['Top', 'Bottom'] : ['Left', 'Right'],
			style_attrs = ['padding', 'border'],
			style_data = {};
		
		// If we are detecting margins	
		if(args[1]){
			style_attrs.push('margin');
		}
		
		$(style_attrs).each(function(){
			
			var $style_attrs = this;
								
			$(dir).each(function(){
				var prop = $style_attrs + this + (($style_attrs == 'border') ? 'Width' : '');
				style_data[prop] = parseFloat($sec_el.css(prop));
			});
			
		});
		
		$el[direction.toLowerCase()]($sec_el[direction.toLowerCase()]());
		$el.css(style_data);
		
		return $el['outer' + direction](args[1]);

	
	}
	
	
	$(['Height', 'Width']).each(function(){
		
		var old_method = jQuery.fn['outer' + this];
		var direction = this;
		
		jQuery.fn['outer' + this] = function(){
			
			if(typeof arguments[0] === 'string'){
				return _outerSetter.call(this, direction, arguments);
			}
			
			return old_method.apply(this, arguments);
		
		}
		
	});
	
	
})(jQuery);

// Examples
/*
$('#myDiv').outerWidth('#myDiv2', true);
$('#myDiv').outerHeight('#myDiv2', true);
*/