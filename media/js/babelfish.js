$(document).ready(function() {
    try
    {
        languages
        fields
        
        for( var i in fields )
        {
            var field = fields[i];
            setupFieldForLanguages( field, languages );
        }
        
        initTabs();
    }
    catch(e)
    {
    }
});
function initTabs()
{
    $(".babelfish-language").click(function(){
        select( 0, this );      
    });
    
    $(".babelfish-language.default").each( select );
}
function select( i, o )
{
    var self = $(o);
    var parent = self.parent();
        
    parent.children().removeClass("selected");
    self.addClass("selected");
    
    var id = self.attr( "rel" );
    var target = $("#" + id );
    var targetParent = target.parent();
    
    targetParent.children().hide();
    target.show();
}

function setupFieldForLanguages( field, languages )
{
    var hfield = $("#id_" + field );
    var p = hfield.parent();
    hfield.remove();
    
    var fields = [hfield];
    for( var i in languages )
    {
        var lang = languages[i][0];
        var f = hfield.clone();
        f.attr( "id", hfield.attr("id") + "_" + lang );
        f.attr( "name", hfield.attr("name") + "_" + lang );
        
        var value = "";
        
        if( translations[lang] && translations[lang][field] )
            value = translations[lang][field];
            
        var nodeName = f[0].nodeName.toLowerCase();
        if( nodeName == "input" )
            f.attr("value",value);
        else if( nodeName == "textarea" )
            f.text(value);
        
        fields.push( f );
    }
    var tab = getTabForFields( fields, [['default','Default']].concat( languages ) );
    p.append( tab );
}
function getTabForFields ( fields, languages )
{
    var l = fields.length;
    
    var div = $("<div></div>");
    var languages_bar = $("<div></div>");
    var languages_widgets = $("<ul></ul>");
    
    div.append( languages_bar );
    div.append( languages_widgets );
    
    for( var i = 0; i<l; i++ )
    {
        var field = fields[i];
        var lang = languages[i][0];
        var langName = languages[i][1];
        var id = field.attr("id");
        
        var li = $("<li class='babelfish-widget' id='li_" + id + "'> (" + langName + ")</li>");
        var a = $("<a href='#' class='babelfish-language "+ lang +"' rel='li_" + id + "'>" + lang + "</a>")
        
        li.prepend( field );
        languages_bar.append( a );
        languages_widgets.append( li );
    }
    return div;
}

