
            
            function toTitleCase(str) {
                return str.replace(
                    /\w\S*/g,
                    function(txt) {
                    return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
                    }
                );
            }
            const formatter = new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'CLP',
            });

            function fill_card_pedido(data, divid) {
                var totalLista = 0;
                var num_items   = 0;
                

                $.each(data, function (i, item) {
                    var trHTML = '';
                    var id          =  item.item_product_slug;
                    var url         =  url_detalle.replace('123', id);
                    num_items       += 1;
                    eltexto         = 'Lista - ' + num_items + ' items';
                    $("#numItems").text(eltexto);

                    $("#totalProductos").text(eltexto);

                    i_linea_01  =   '<div class="row" id="' + item.item_id + '">' + 
                                        '<div class="col" style="width: 18rem;">'+
                                            '<div class="card ">' +
                                                '<div class="card-header">' +
                                                    '<div class="float-start">' +
                                                        '<small>' +  toTitleCase(item.marca) + '</small> ' +
                                                    '</div>' +
                                                '</div>' +
                                                '<div class="card-body text-center">' +
                                                    '<img src="' + item.imagen +  '" class="card-img-top img-thumbnail rounded" alt="' + toTitleCase(item.nombre) + '" style="width:50%;"/>' +
                                                '</div>' +
                                                '<div class="card-body">' +
                                                    '<div class="float-start">' +
                                                        '<h5 class="card-title">' + toTitleCase(item.nombre)  + '</h5>' +
                                                    '</div>';
                                                // '</div>'; 
                                    //             +
                                    //         '</div>' +
                                    //     '</div>'+
                                    // '</div>';

                    
                    
                    var grados              = '';
                    var color               = '';
                    var unidades            = '';
                    var medida              = '';
                    var envase              = '';
                    var dimension           = '';

                    if (item.grados){
                        grados              = '<span class="text-primary"> • </span><span>' +  item.grados + '° </span>';
                    }
                    if (item.envase) {
                        envase              = '<span class="text-primary"> • </span><span>' +  item.envase + '</span>';
                    }
                    if (item.color) {
                        color               = '<span class="text-primary"> • </span><span>Color: ' +  item.color + '</span>';
                    }
                    if (item.unidades !=1 ){
                        unidades            = '<p><span class="badge badge-info">' + item.unidades + ' Unidades </span>' +
                                            '</p>';  
                    }
                    if (item.medida_cant !=1 ){
                        medida            = '<span class="text-primary"> • </span><span>' +  item.medida_cant + ' ' + item.medida_um  + '</span>';
                    }
                    if (item.dimension){
                        dimension       = '<span class="text-primary"> • </span><span>' +  item.dimension  + '</span>';
                    }


                    // linea_data          =   '<div class="card-body">' + 
                    // linea_data          =      '<div class="mt-1 mb-0 text-muted small">'  + 
                    linea_data          =           grados + 
                                                    medida + 
                                                    envase +  
                                                    color + 
                                                    dimension  + 
                                                    unidades +
                                                    '<br/>'  +
                                                '</div>' ;
                                            // '</div>' ;

                    
                    linea_subtotal      = '<p class="text-start text-md-center"><strong>' + formatter.format(item.item_subtotal) + '</strong></p>';


                    botones_inicio      =   '<div class="row" >' +
                                                '<div class="col-6 align-items-center" >' +
                                                    '<button class="LessProduct btn btn-primary px-3 me-2" id_prod="' + item.item_id + '"><i class="bi bi-dash-lg" ></i></button>' +
                                                    '<label class="form-label" for="form1">'+ item.item_quantity +  '</label>' +
                                                    '<button class="MoreProduct btn btn-primary px-3 ms-2" id_prod="' + item.item_id + '"><i class="bi bi-plus-square"></i></button>' +
                                                '</div>' +
                                                '<div class="col-6 align-items-center" >' +
                                                    '<button type="button" class="btn btn-danger  px-3 ms-2" data-mdb-toggle="tooltip" title="Elminar item">' + '<i class="RemoveProduct bi bi-trash" id_prod="'  + item.item_id + '"></i>' + '</button>'+
                                                '</div>'+
                                            '</div>';
                    

                    linea_cantidad      = '<div class="container my-3">'  + botones_inicio   +'</div>';

                    f_linea_01          = '</div></div>';

                    f_row       = '<hr class="my-4" />';
                    trHTML +=  
                        i_linea_01 + 
                        linea_data +
                        linea_cantidad +
                        f_linea_01 ;
                        // f_row ;
                    $(divid).append(trHTML);
                })
                
            }
            

            function fill_datat_prods(data, domid){
                // Head
                linea1              = '<tr>' +
                    '<th>Articulo</th>' +
                    '<th class="text-end">Precio</th><th class="text-end">Total</th></tr>';

                $.each(data.tableProd2, function (i, item3) {
                    grados              = '';

                    if (item3.cambio){
                        iniciotr = '<tr id="' + item3.item_id + '" class="text-success">';
                    } else {
                        iniciotr = '<tr id="' + item3.item_id + '">';
                    }
                    
                    if (item3.grados){
                        grados              =  ' ' + item3.grados + '°';
                    }


                    articulo        = '<td>' + item3.item_quantity + ' ' + toTitleCase(item3.marca) + ':' + item3.nombre  + ' ' + grados + ' '  + item3.color + ' ' + item3.dimension + '</td>';
                    precio          = '<td class="text-end">' + item3.item_price + '</td>'
                    totallinea      = '<td class="text-end">' + formatter.format(item3.item_subtotal) + '</td>';
                    fintr           = '</tr>';
                    linea2  = iniciotr  +
                        articulo +
                        precio +
                        totallinea +
                        fintr;
                    linea1 = linea1 + linea2;


                })
                return linea1;

            }
            

            function echoinfo(data,  detalle) {
                // alert(detalle.grantotalunidades)
                // Busco super mas barato
                var valormasbajo = 99999999;
                var que_sitio_id = 0;

                // Quienes tienen todos los productos
                $.each(data, function (e, suoer) {
                    // console.log('detalle.grantotalunidades=',detalle.grantotalunidades, ' vs ', suoer.supertotalunidades );

                    if (flag_costo_despacho=='true'){
                        if (detalle.grantotalunidades == suoer.supertotalunidades){
                            total_super = Number(suoer.totcompra)  +  Number(suoer.valor_despacho );
                            // console.log('Entra a costo de despacho true, total_super=', suoer.totcompra, suoer.valor_despacho);
                            if ( valormasbajo > total_super &&  (Number(suoer.totcompra) > Number(suoer.monto_minimo_compra))) {
                                valormasbajo = total_super;
                                que_sitio_id = suoer.id;
                                // console.log('Ok',que_sitio_id )
                            }
                        }
                    } else {
                        if (detalle.grantotalunidades == suoer.supertotalunidades){
                            if ( valormasbajo > Number(Number(suoer.totcompra)  ) ) {
                                valormasbajo = Number(Number(suoer.totcompra)  ) ;
                                que_sitio_id = suoer.id;
                            }
                        }
                    }
                })
                
                // console.log(que_sitio_id);
                var trHTML         = '';
                $.each(data, function (i, suoer) {
                    var nota = "";
                    var clase = "";

                    var expanded = "false";
                    var expanded_class = "";
                    var button_checkout_class = "disabled";
                    var productos_que_faltan = detalle.grantotalunidades - suoer.supertotalunidades;
                    // console.log('productos_que_faltan', productos_que_faltan);
                    if (flag_costo_despacho=='true'){
                        if (Number(suoer.totcompra) > Number(suoer.monto_minimo_compra)) {
                            if (que_sitio_id == suoer.id ){
                                clase = "bg-success text-white";
                                nota = "El mejor";
                                nota_titulo = "";
                                expanded = "true";
                                expanded_class = "show";
                                button_checkout_class = "";
                            } else {
                                if (detalle.grantotalunidades == suoer.supertotalunidades){
                                    clase = "bg-danger text-white";
                                    nota = "Mas caro";
                                    nota_titulo = "Caro";
                                    button_checkout_class = "";
                                    
                                } else {
                                    nota = "No tiene todos los productos. Faltan " + productos_que_faltan;
                                    clase = "bg-info text-dark";
                                    nota_titulo = "Faltan " + productos_que_faltan +" productos";
                                    button_checkout_class = "disabled";
                                }
                            }
                        } else {
                            nota = "No alcanza compra mínima de " + formatter.format(suoer.monto_minimo_compra);
                            nota_titulo = "Compra mínima de " + formatter.format(suoer.monto_minimo_compra);
                            clase = "bg-info text-dark";
                            supernoalcanza = supernoalcanza + 1;
                        }
                    } else {
                        if (que_sitio_id == suoer.id ){
                            // || suoer.requerido
                            clase = "bg-success text-white";
                            nota = "El mejor";
                            nota_titulo = "";
                            expanded = "true";
                            expanded_class = "show";
                            button_checkout_class = "";
                        } else {
                            if (detalle.grantotalunidades == suoer.supertotalunidades){
                                clase = "bg-danger text-white";
                                nota = "Mas caro";
                                nota_titulo = "Caro";
                                button_checkout_class = "";
                                
                            } else {
                                nota = "No tiene todos los productos. Faltan " + productos_que_faltan;
                                clase = "bg-info text-dark";
                                nota_titulo = "Faltan " + productos_que_faltan +" productos";
                                button_checkout_class = "disabled";
                            }
                        }
                    }
                    
                    super_dom_id = 'table_' + suoer.supermercados.areaDespacho_despachoid;


                    super_table = '<div class="table-responsive">' +
                                    '<table class="table table-bordered table-sm" id="' + super_dom_id + '">' +
                                        '<thead><tr></tr></thead>' +
                                        '<tbody>'+
                                            fill_datat_prods(suoer, super_dom_id) +
                                        '</tbody>' +
                                    '</table>    </div>';


                    // console.log(suoer.supermercados.areaDespacho_dias);
                    var  dias, horas, despacho, add_resumen = '';
                    var  costo_despacho = 0;

                    if (flag_costo_despacho=='true'){
                        

                        $.each(suoer.supermercados.areaDespacho_dias, function (i, momento) {
                            dias = momento.dias;
                            horas= momento.horas;
                        })

                        despacho = '<p><strong>Días y horas de despacho</strong></p>'+
                            '<p>' + dias + '</p>' +
                            '<p class="mb-0">' + horas +'</p>';

                        add_resumen = '<li class="list-group-item d-flex justify-content-between align-items-center px-0">' +
                            ' Despacho  ' +
                            '<span>' + formatter.format(suoer.supermercados.areaDespacho_valor_despacho) + '</span>' +
                            '</li>' ;
                        costo_despacho = suoer.supermercados.areaDespacho_valor_despacho;
                        total_supe = suoer.supermercados.areaDespacho_valor_despacho + suoer.totcompra;
                        notas_despacho = '<i class="bi bi bi-exclamation-diamond" title="Mínimo de compra"></i> ' +  formatter.format(suoer.supermercados.areaDespacho_monto_minimo_compra) +  ' ' +
                                        '<i class="bi bi-truck" title="Costo despacho"></i> ' + formatter.format(suoer.supermercados.areaDespacho_valor_despacho) + ' ' ;
                    } else {
                        total_supe =  suoer.totcompra;
                        despacho = '';
                        notas_despacho = '';
                    }
                    

                    resumen = '<div class="card-body">'+
                                '<ul class="list-group list-group-flush"><li class="list-group-item d-flex justify-content-between align-items-center border-0 px-0 pb-0">Productos<span id="totalProductos">'  + formatter.format(suoer.totcompra) + '</span></li>' +
                                add_resumen +
                                '<li class="list-group-item d-flex justify-content-between align-items-center border-0 px-0 mb-3">' +
                                    '<div><strong>Total Supermercado</strong></div>' +
                                    '<span><strong>'  + formatter.format(costo_despacho + suoer.totcompra) + '</strong></span></li></ul>'  +
                                // '<button type="button" class="btn btn-primary btn-lg btn-block ' + button_checkout_class +  '">Go to checkout</button>' + 
                                '</div>';


                    linea_03    = '<div class="accordion-item ">'+
                                        '<h2 class="accordion-header" id="super_'  +  suoer.supermercados.areaDespacho_despachoid  +'">'  +
                                            '<button class="accordion-button  ' +  clase +  '" type="button" data-bs-toggle="collapse" data-bs-target="#collapse' + suoer.supermercados.areaDespacho_despachoid  +'" aria-expanded="' +  expanded  +'" aria-controls="collapseOne">' +
                                                '<i class="bi bi-shop-window"></i> &nbsp;' + suoer.supermercados.areaDespacho_siteName + '&nbsp;' +
                                                ' <span class="badge badge-primary text-bg-warning rounded-pill">' + nota_titulo  + '</span>' +
                                                ' <span class="badge badge-primary rounded-pill">' + formatter.format(total_supe) + '</span>' +
                                            '</button>' +
                                        '</h2>' +
                                        '<div id="collapse' + suoer.supermercados.areaDespacho_despachoid +  '" class="accordion-collapse collapse ' + expanded_class + '" aria-labelledby="super_'  + suoer.areaDespacho_despachoid +  '" data-bs-parent="#accordionSuper">' +
                                            '<div class="accordion-body">' +
                                                '<p>'  +
                                                    notas_despacho + 
                                                    '<i class="bi bi-sticky" title="' + nota +'"></i>  ' + nota + 
                                                '</p>'+
                                                super_table +
                                                resumen  +
                                                despacho +
                                            '</div>' +
                                        '</div>'  +
                                    '</div>';

                    $("#accordionSuper").append(linea_03);


                });
                
                var supernoalcanza = 0;
                $.each(data, function (e, suoer) {
                    if (Number(suoer.totcompra) > Number(suoer.monto_minimo_compra)) {

                    } else {
                        supernoalcanza = supernoalcanza + 1;
                    }
                })
                var eltexto = '';
                if (flag_costo_despacho=='true'){
                    if (supernoalcanza !=0){
                        eltexto = supernoalcanza + ' supermercados que no se alcanza el mínimo para hacer despacho.' ;
                    }
                }
                $("#supermercadosnominimo").text(eltexto);
            };

            function borratablas() {
                $("#card-pedidos").find("div:gt(0)").remove();
                $("#card-pedidos").find("hr").remove();

                $("#accordionSuper").find("div").remove();
                $("#resummen_super2").find("li").remove();
            };

            function superinfo(superdetail) {
                $("#supermercadoscount").text(superdetail.supermercadoscount);
                var eltexto = superdetail.supersinproductos + ' que no tienen ningun Producto.';
                $("#supermercadossinprod").text(eltexto);
            };

            function carritoinfo(superdetail) {
                $("#products-quantity").text(superdetail.itemsInCart);
            };

            function loadCarritoCompleto(data, table) {
                var jqxhr =  $.ajax({
                    url: url_get_cart,  
                    type: "POST",
                    async: false,
                    data: {
                        'product': 0,
                        'quantity': "1",
                        'totcompra': 0,
                        'csrfmiddlewaretoken': csrf_token,
                    }})

                    .done(function(data){
                        var flag_costo_despacho = get_costo_despacho();
                        borratablas();
                        fill_card_pedido(data.prods, '#card-pedidos');
                        echoinfo(data.totsuper, data.superdetail);
                        superinfo(data.superdetail);
                        carritoinfo(data.superdetail);
                    })

                    .fail(function() {
                        alert( "error" );
                    })
            };
            function loadCarrito(data, table) {
                var jqxhr =  $.ajax({
                    url: url_get_cart_siple,
                    type: "POST",
                    data: {
                        'product': 0,
                        'quantity': "1",
                        'totcompra': 0,
                        'csrfmiddlewaretoken': csrf_token,
                    }})

                    .done(function(data){
                        carritoinfo(data.superdetail);
                    })
                    .fail(function() {
                        alert( "error" );
                    })
            };  
            function sayToast(texto,tipo){
                if (tipo=='good') {
                    $.toast({
                        heading: 'Exito',
                        text: texto,
                        showHideTransition: 'slide',
                        icon: 'success',
                        loader: true,        // Change it to false to disable loader
                        loaderBg: '#9EC600'  // To change the background
                    });
                } else if (tipo=='bad'){
                    $.toast({
                        heading: 'Error',
                        text: texto,
                        showHideTransition: 'slide',
                        icon: 'error',
                        loader: true,        
                        loaderBg: '#9EC600'  
                    });
                } else if (tipo=='info'){
                    $.toast({
                        heading: 'Info',
                        text: texto,
                        showHideTransition: 'slide',
                        icon: 'info',
                        loader: true,        
                        
                    });
                }
                
            };

            $(document).on('change', '.order-by-input', function() {
                $( "form" ).submit();
            });
            $(document).on('click', '.RemoveProduct', function() {
                var id_prod = $(this).attr("id_prod");
                
                var jqxhr =  $.ajax({
                    url: url_removeproduct, 
                    type: "POST",
                    data: {
                        'product': id_prod,
                        'quantity': "1",
                        'totcompra': 0,
                        'csrfmiddlewaretoken': csrf_token,
                    }})

                .done(function(data){
                    borratablas();
                    fill_card_pedido(data.prods, '#card-pedidos');
                    echoinfo(data.totsuper,data.superdetail);
                    sayToast('Producto eliminado de su lista.','good');
                    carritoinfo(data.superdetail);
                })
                
                .fail(function() {
                    sayToast('No se agrego a lista.','bad');
                })
            });


            $(document).on('click', '.MoreProduct', function() {
                var id_prod = $(this).attr("id_prod");
                
                var jqxhr =  $.ajax({
                    url: url_increase_product,
                    type: "POST",
                    data: {
                        'product': id_prod,
                        'quantity': "1",
                        'totcompra': 0,
                        'csrfmiddlewaretoken': csrf_token,
                    }})

                .done(function(data){
                    borratablas();
                    fill_card_pedido(data.prods, '#card-pedidos');
                    echoinfo(data.totsuper,data.superdetail);
                    sayToast('Producto aumentado en su lista.','good');
                    carritoinfo(data.superdetail);
                })

                .fail(function() {
                    sayToast('No se agrego a lista.','bad');
                })
            });

            $(document).on('click', '.LessProduct', function() {
                var id_prod = $(this).attr("id_prod");
                
                var jqxhr =  $.ajax({
                    url: url_decrementproduct,
                    type: "POST",
                    data: {
                        'product': id_prod,
                        'quantity': "1",
                        'totcompra': 0,
                        'csrfmiddlewaretoken': csrf_token,
                    }})

                .done(function(data){
                    borratablas();
                    fill_card_pedido(data.prods, '#card-pedidos');
                    echoinfo(data.totsuper,data.superdetail);
                    sayToast('Producto disminuido de su lista.','good');
                    carritoinfo(data.superdetail);    
                })

                .fail(function() {
                    sayToast('Error .','bad');
                })
            });
            //     
            
            $(document).on('click', '#clean_list', function() {
                var jqxhr =  $.ajax({
                    url: url_emptycart,
                    type: "POST",
                    data: {
                        'csrfmiddlewaretoken': csrf_token,
                    }})

                .done(function(data){
                    borratablas();
                    sayToast('Lista borrada.','good');
                    carritoinfo(data.superdetail);
                })

                .fail(function() {
                    sayToast('Error .','bad');
                })
                
            });

            $(document).on('click', '#save_list', function() {
                var nombre_lista = $("#nombre_lista").val();
                var public = $("#public").is(":checked");
               
                var jqxhr =  $.ajax({
                    url: url_save_cart,
                    type: "POST",
                    data: {
                        'nombre_lista': nombre_lista,
                        'public': public,
                        'csrfmiddlewaretoken': csrf_token,
                    }})

                .done(function(data){
                    sayToast('Lista almacenada.','info');
                })

                .fail(function() {
                    sayToast('Error .','bad');
                })

                $("#myModal").modal('hide');

            });
            $(document).on('click', '.AddProduct', function() {
                $("#spnniinner1").show();
                var id_prod = $(this).attr("id_prod");
                
                var jqxhr =  $.ajax({
                    url: url_add_product,
                    type: "POST",
                    data: {
                        'product': id_prod,
                        'quantity': "1",
                        'csrfmiddlewaretoken': csrf_token,
                    }})
                .done(function(data){
                    sayToast('Producto agregado a su lista.','good');
                    $("#spnniinner1").delay(800).fadeOut();
                    carritoinfo(data.superdetail);
                    $(this).button("toggle");
                    $(this).hide();
                    
                })
                .fail(function() {
                    sayToast('Error .','bad');
                    $("#spnniinner1").delay(400).fadeOut();
                })
            });


