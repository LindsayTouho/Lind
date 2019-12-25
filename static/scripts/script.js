function log(p){
    console.log(p)
}

function writeLocaion(name, str){
    str = str.replace(/\\\//g,'/');
    localStorage.setItem(name, str);
}

function save_article(e){
    var id = -1;
    if($("#id").length!==0){
        id = $("#id")[0].value;
    }
    $.ajax({
            url: "/admin/save/",
            data: {
                id: id,
                content: localStorage.getItem("writing"),
                // title: $("#title")[0].value,
                // tags: $("#tags")[0].value,
                // update_time: $("#update_time").is(":checked")
            },
            type: "POST",
            dataType: "JSON"
        }
    ).done(function(json){
        if(json['message']==="Saved"){
            $("#id").remove();
            var id = $("<input type='hidden' value='"+json['id']+"' id='id'> ");
            $("body").append(id);
            flash("保存成功");
        }
        else{
            flash("保存失败: "+json['message']);
        }
    }
    );
}

function flash(message) {
    M.toast({html:message});
}

function init_katex() {
    blocks = document.getElementsByClassName("article_block");
    for(var i=0; i !== blocks.length; ++i){
        renderMathInElement(blocks[i],{
             delimiters: [
                 {left: "$$", right: "$$", display: true},
                 {left: "\\[", right: "\\]", display: true},
                 {left: "$", right: "$", display: false},
                 {left: "\\(", right: "\\)", display: false}
            ],
            ignoredClasses: ["no_latex",]
        });
    }
}

function init_pjax() {
    $(document).pjax('a', '#main', {'timeout':5000});
    $(document).on('pjax:success',function () {
        init_katex();
        M.AutoInit();
    });
    $(document).on('pjax:clicked',function () {
        $('#main').html("<div class=\"preload-container\"><div class=\"preloader-wrapper big active\">\n" +
            "    <div class=\"spinner-layer spinner-blue-only\">\n" +
            "      <div class=\"circle-clipper left\">\n" +
            "        <div class=\"circle\"></div>\n" +
            "      </div><div class=\"gap-patch\">\n" +
            "        <div class=\"circle\"></div>\n" +
            "      </div><div class=\"circle-clipper right\">\n" +
            "        <div class=\"circle\"></div>\n" +
            "      </div>\n" +
            "    </div>\n" +
            "  </div>");
    });
}

// function init_comments() {
//     var gitalk = new Gitalk({
//         clientID: '95b11f155d07ad637d61',
//         clientSecret: '8ac4c306a6b11daccc4392e4250cc1c499cd8761',
//         repo: 'Blog-Comments',
//         owner: 'LindsayTouho',
//         admin: ['LindsayTouho'],
//         id: location.pathname,      // Ensure uniqueness and length less than 50
//         // distractionFreeMode: false  // Facebook-like distraction free mode
// })

// gitalk.render('gitalk-container')
// }

function on_load() {
    $(".del_article").on("click", del_article);

    init_katex();
    init_pjax();


    // $('.sidenav').sidenav();
    // $('.collapsible').collapsible();
    // $('.materialboxed').materialbox();
    M.AutoInit();
}

function  del_article(e) {
    if( !confirm("确定删除这篇文章吗？")){
        e.preventDefault();
    }
}



$(function (){
    on_load();
});