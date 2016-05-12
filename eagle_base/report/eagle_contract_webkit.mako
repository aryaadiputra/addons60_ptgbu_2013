<html>
<head>
    <style type="text/css">
        ${css}
    </style>
<script>
var sommeHT=0;
var sommeTax=0;
var sommeTotal=0;
</script>
</head>
<body>

    <%
    def carriage_returns(text):
        return text.replace('\n', '<br />')
    %>

    %for inv in objects :
    <% setLang(inv.customer_id.lang) %>
    <table class="dest_address">
        <tr><td ><b>${inv.customer_id.name |entity} ${inv.customer_id.title.name or ''|entity}</b></td></tr>
        <tr><td>${inv.customer_id.address[0].street or ''|entity}</td></tr>
        <tr><td>${inv.customer_id.address.street2[0] or ''|entity}</td></tr>
        <tr><td><u>${inv.customer_id.address.zip[0] or ''|entity} ${inv.customer_id.address.city[0] or ''|entity}</u></td></tr>
    </table>
    <br />   

<br/><br/>
 
 <table class="list_table" width="100%">
<tr style="height:20;">
      <td width="50%" style="border-bottom:1px solid; border-color: #0066FF;"><b>Description</b></td>
      <td class width="10%" style="border-bottom:1px solid; border-color: #0066FF;text-align:right;"><b>Quantit&eacute;</b></td>
      <td class width="7%" style="border-bottom:1px solid; border-color: #0066FF;text-align:right;"><b>${_("Uom")}</b></td>	
      <td style="border-bottom:1px solid; border-color: #0066FF;text-align:right;" width="13%"><b>Prix Unitaire</b></td>
      <!--<td style="border-bottom:1px solid; border-color: #0066FF;text-align:right;" width="10%"><b>Taxe</b></td>-->
      <td style="border-bottom:1px solid; border-color: #0066FF;text-align:right;" width="10%"><b>Montant</b></td></tr>

        %for line in inv.positions :
           %if line.state == "open" or line.state == 'recurrent':

<script>
sommeHT += ${float(line.cl_amount)};
sommeTax += ${float(line.cl_taxes)};
sommeTotal += ${float(line.cl_total)};
</script>
        <tr style="height:30;padding-top:5px;">
		<td><b>${line.out_description or ''|entity}</b></td>
                <td style="text-align:right;">${line.qty or '0'}</td>
              %if line.name and line.name.product_tmpl_id.uom_id:
		<td style="text-align:right;">${line.name.product_tmpl_id.uom_id.name or ''|entity}</td>
		%else :
		<td>&nbsp;</td>
		%endif
                <td style="text-align:right;">${line.name.lst_price or '0.00'}</td>
                <!--<td style="text-align:right;">${line.cl_taxes or '0.00'}</td>-->
                <td style="text-align:right;">${line.cl_amount or '0.00'}</td>
        </tr>

%if line.notes :
<tr>
      <td colspan="3" style="border-style:none;  font-size:11px;">${line.notes | carriage_returns}</td>
      <td colspan="2" style="border-style:none;"> </td>
</tr>       
%endif

%endif

%endfor

<tr>
      <td colspan="5" style="border-style:none;"><br/></td>
</tr>
<tr>
      <td colspan="5" style="border-style:none;"><br/></td>
</tr>
 <tr  style="height:20;">
       <td style="border-style:none;"/>
       <td style="border-top:1px solid; border-color: #0066FF;">Hors Taxe</td>
       <td style="border-top:1px solid; border-color: #0066FF;"/>
        <td style="border-top:1px solid; border-color: #0066FF;"/>CHF</td>
        <td style="border-top:1px solid; border-color: #0066FF;text-align:right"><script>document.write (sommeHT.toFixed(2));</script></td>
</tr>
 <tr  style="height:20;">
       <td style="border-style:none;"/>
       <td style="border-top:1px solid; border-color: #0066FF;">TVA</td>
       <td style="border-top:1px solid; border-color: #0066FF;"/>
      <td style="border-top:1px solid; border-color: #0066FF;"/>
        <td style="border-top:1px solid; border-color: #0066FF;text-align:right"><script>document.write (sommeTax.toFixed(2));</script></td>
</tr>
        <tr style="height:20;">
        <td style="border-style:none;"/>
        <td style="border-top:1px solid; border-color: #0066FF;"><b>Total TTC</b></td>
        <td style="border-top:1px solid; border-color: #0066FF;"/>
        <td style="border-top:1px solid; border-color: #0066FF;"/>CHF</td>
        <td style="border-top:1px solid; border-color:#0066FF;text-align:right"><script>document.write (sommeTotal.toFixed(2));</script></td>
</tr>
<tr>
      <td colspan="5" style="border-style:none;"><br/></td>
</tr>

%if inv.notes :
<tr>
      <td colspan="3" style="border-style:none;">${inv.notes | carriage_returns}</td>
      <td colspan="2" style="border-style:none;"> </td>
</tr>       
%endif

        </tbody>
    </table>

    <p style="page-break-after:always"></p>
    %endfor
</body>
</html>