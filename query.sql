select ean_13, id, nombre, marca_id from precios_articulos where ean_13 in (select ean_13 from precios_articulos where ean_13 <> "" group by ean_13 having count(1) > 1 order by ean_13) order by ean_13;



select ean_13, precios_articulos.id, precios_articulos.nombre, marca_id, precios_marcas.nombre, precios_articulos.grados, precios_articulos.envase from precios_articulos inner join precios_marcas on precios_articulos.marca_id = precios_marcas.id where ean_13 in (select ean_13 from precios_articulos where ean_13 <> "" group by ean_13 having count(1) > 1 order by ean_13) order by ean_13;



select ean_13, precios_articulos.id, precios_articulos.nombre, marca_id, precios_marcas.nombre, precios_articulos.grados, precios_articulos.unidades from precios_articulos inner join precios_marcas on precios_articulos.marca_id = precios_marcas.id where ean_13 in (select ean_13 from precios_articulos where ean_13 <> "" group by ean_13 having count(1) > 1 order by ean_13) order by ean_13;

select 
    ean_13, 
    precios_articulos.id, 
    precios_articulos.nombre, 
    marca_id, 
    grados2,
    precios_marcas.nombre, 
    precios_articulos.grados, 
    precios_articulos.unidades 
from precios_articulos 
inner join 
    precios_marcas 
    on precios_articulos.marca_id = precios_marcas.id 
where ean_13 in (
    select ean_13 from precios_articulos where ean_13 <> "" group by ean_13 having count(1) > 1 order by ean_13
    ) 
order by ean_13;

select 
    ean_13, 
    marca_id
from precios_articulos where ean_13 <> "" group by ean_13 having count(1) > 1 order by ean_13;

select 
    ean_13, 
    marca_id
from precios_articulos where ean_13 <> "" group by marca_id having count(1) = 1 order by ean_13;

---
select 
    ean_13, 
    precios_articulos.id, 
    precios_articulos.nombre, 
    marca_id, 
    precios_marcas.nombre, 
    precios_articulos.grados, 
    precios_articulos.unidades 
from precios_articulos 
inner join 
    precios_marcas 
    on precios_articulos.marca_id = precios_marcas.id 
where 
    ean_13 in (
        select ean_13 from precios_articulos where ean_13 <> "" group by ean_13 having count(1) > 1 order by ean_13
    ) 
    and marca_id in (
        select marca_id from precios_articulos where ean_13 <> "" group by marca_id having count(1) = 1
    )
order by ean_13;

{"@context":"https://schema.org","@graph":[{"@type":"Organization","@id":"https://vettershop.cl/#organization","name":"Vettershop","url":"https://vettershop.cl","sameAs":["https://www.facebook.com/Vettershop-102287032571234"],"logo":{"@type":"ImageObject","@id":"https://vettershop.cl/#logo","url":"https://vettershop.cl/wp-content/uploads/2022/01/vetter-nuevologo-07-e1658778147745.png","contentUrl":"https://vettershop.cl/wp-content/uploads/2022/01/vetter-nuevologo-07-e1658778147745.png","caption":"Vettershop","inLanguage":"es","width":"500","height":"145"}},{"@type":"WebSite","@id":"https://vettershop.cl/#website","url":"https://vettershop.cl","name":"Vettershop","publisher":{"@id":"https://vettershop.cl/#organization"},"inLanguage":"es"},{"@type":"ImageObject","@id":"https://vettershop.cl/wp-content/uploads/2022/07/frutilla.webp","url":"https://vettershop.cl/wp-content/uploads/2022/07/frutilla.webp","width":"1500","height":"1500","inLanguage":"es"},{"@type":"BreadcrumbList","@id":"https://vettershop.cl/producto/mermelada-quilvo-frutilla-420-gr/#breadcrumb","itemListElement":[{"@type":"ListItem","position":"1","item":{"@id":"https://vettershop.cl","name":"Portada"}},{"@type":"ListItem","position":"2","item":{"@id":"https://vettershop.cl/producto/mermelada-quilvo-frutilla-420-gr/","name":"Mermelada Quilvo Frutilla 420 Gr"}}]},{"@type":"ItemPage","@id":"https://vettershop.cl/producto/mermelada-quilvo-frutilla-420-gr/#webpage","url":"https://vettershop.cl/producto/mermelada-quilvo-frutilla-420-gr/","name":"Mermelada Quilvo Frutilla 420 Gr - VetterShop","datePublished":"2023-08-22T09:58:03-04:00","dateModified":"2023-08-23T11:02:26-04:00","isPartOf":{"@id":"https://vettershop.cl/#website"},"primaryImageOfPage":{"@id":"https://vettershop.cl/wp-content/uploads/2022/07/frutilla.webp"},"inLanguage":"es","breadcrumb":{"@id":"https://vettershop.cl/producto/mermelada-quilvo-frutilla-420-gr/#breadcrumb"}},{"@type":"Product","name":"Mermelada Quilvo Frutilla 420 Gr - VetterShop","description":"Mermelada Quilvo Frutilla 420 Gr y muchos otros productos que puedes encontrar en las distintas categor\u00edas disponibles para t\u00ed en nuestro sitio VetterShop","sku":"7804020000667","category":"Supermercado &gt; Abarrotes","mainEntityOfPage":{"@id":"https://vettershop.cl/producto/mermelada-quilvo-frutilla-420-gr/#webpage"},"offers":{"@type":"Offer","price":"4890","priceCurrency":"CLP","priceValidUntil":"2024-12-31","availability":"https://schema.org/InStock","itemCondition":"NewCondition","url":"https://vettershop.cl/producto/mermelada-quilvo-frutilla-420-gr/","seller":{"@type":"Organization","@id":"https://vettershop.cl/","name":"Vettershop","url":"https://vettershop.cl","logo":"https://vettershop.cl/wp-content/uploads/2022/01/vetter-nuevologo-07-e1658778147745.png"}},"@id":"https://vettershop.cl/producto/mermelada-quilvo-frutilla-420-gr/#richSnippet","image":{"@id":"https://vettershop.cl/wp-content/uploads/2022/07/frutilla.webp"}}]}


- Venta de articulos con su codigo de barra

 Coca-Cola
Re-Scan 36254108

 Coca-Cola
Re-Scan 36262571

select     ean_13,     marca_id from precios_articulos where ean_13 = '80432402672';