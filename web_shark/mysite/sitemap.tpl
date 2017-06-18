<?xml version="1.0" encoding="UTF-8"?>

<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

    <url>
        <loc>http://sharkevo.ru/</loc>
        <lastmod>{{curtime}}</lastmod>
    </url>

    {% for m in res %}
    <url>
        <loc>http://sharkevo.ru/{{m[0]}}</loc>
        <lastmod>{{m[1]}}</lastmod>
    </url>
    {% endfor %}

</urlset>
