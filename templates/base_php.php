<?php
    // PHP Template with Jinja2 integration
    $FEEDBACK_CODE = "review_{{product_code|default('product_code')}}"; // 半角64文字まで
    $FEEDBACK_TXT = "{{product_name|default('商品名')}}のレビューは参考になりましたか？";
    $title_tag = "{{product_name|default('商品名')}}のレビュー｜アダルトグッズ・大人のおもちゃ通販ショップ｜NLS";
    $keywords_tag = "{{product_name|default('商品名')}},アダルトグッズ,大人のおもちゃ,通販,NLS";
    $description_tag = "{{product_name|default('商品名')}}のレビュー｜{{category|default('カテゴリ')}}｜{{category|default('カテゴリ')}}｜{{category|default('カテゴリ')}}【アダルトグッズ｜NLS】豊富な商品のクチコミが掲載されています。経験豊富な女性スタッフが、あなたにぴったりの大人のおもちゃをお選びします。";
    
    include_once("../../inc_header_fix.php");
    include_once("$NLS_INCLUDE_DIR/review/{{product_code|default('product_code')}}/{{product_code|default('product_code')}}.html");
    include_once("../../content/hotitem/question.php");
    include_once("../../inc_footer_fix.php");
?>