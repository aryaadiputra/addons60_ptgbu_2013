<html>
<body>
<%get_data(data)%>
<%x = get_filter(data)%>
<% setLang('en_US' or 'en_ID' ) %>
<table width=100% border="0" cellscpacing="0" cellpadding="0" style="font-family:arial;font-size:12px";>
	<tr >
		<td colspan="6" style="text-align: center">
			<tr>
				<td colspan="6" style="text-align: center">PT GUNUNG BARA UTAMA ${x}</td>
			</tr>
			<tr>
				<td colspan="6" style="text-align: center">Balance Sheet</td>
			</tr>
			<tr>
				<td colspan="6" style="text-align: center">-</td>
			</tr>
			<tr>
				<td colspan="6" style="text-align: center">(in Indonesian Rupiah)</td>
			</tr>
		</td>
	</tr>
	<tr>
		<td colspan="3" style="text-align: center">&nbsp</td>
		<td style="text-align: center">&nbsp</td>
		<td style="text-align: center">DATE</td>
		<td style="text-align: center">DATE</td>
	</tr>
	<tr>
		<td colspan="3" style="text-align: center"></td>
		<td style="text-align: center">Notes</td>
		<td style="text-align: center">Rp.</td>
		<td style="text-align: center">Rp.</td>
	</tr>
<%
	level3_no 	= 0
	lv3_name	= ""
	lv3_total	= 0.0
	lv3_total2	= 0.0
	total_asset = 0.0
	total_asset2 = 0.0
%>

%for lines in get_lines_another('asset'):
	%if lines['type'] == 'view' and lines['level'] == 2:
		<tr>
			<td></td>
			<td colspan="2" style="text-align: center">${lines['name']}</td>
			<td colspan="3"></td>
		</tr>
		<tr>
			<td colspan="6">&nbsp</td>
		</tr>
	%endif
	%if lines['type'] == 'view' and lines['level'] == 3:
		<% level3_no+=1 %>
		<% total_asset += lv3_total %>
		<% total_asset2 += lv3_total2 %>
		%if lv3_name <> "":
			<tr>
				<td>&nbsp</td>
				<td colspan="2"></td>
				<td></td>
				<td></td>
				<td></td>
			</tr>
			<tr>
				<td></td>
				<td colspan="2">Total ${lv3_name}</td>
				<td></td>
				<td style="text-align: right">${formatLang(int(lv3_total),digits=get_digits(dp='Account'))}</td>
				<td style="text-align: right">${formatLang(int(lv3_total2),digits=get_digits(dp='Account'))}</td>
			</tr>
			<tr>
				<td colspan="6">&nbsp</td>
			</tr>
			<tr>
				<td colspan="6">&nbsp</td>
			</tr>
		%endif
		<tr>
			<td>${level3_no}</td>
			<td colspan="2">${lines['name']}</td>
		</tr>
		<tr>
			<td colspan="6">&nbsp</td>
		</tr>
		<% lv3_name =  lines['name']%>
		<% lv3_total =  lines['balance']%>
		<% lv3_total2 =  lines['balance2']%>
	%endif
	
	%if lines['type'] == 'view' and lines['level'] == 4:
		<tr>
			<td></td>
			<td width="40"></td>
			<td>${lines['name']}</td>
			<td></td>
			<td style="text-align: right">${formatLang(int(lines['balance']),digits=get_digits(dp='Account'))}</td>
			<td style="text-align: right">${formatLang(int(lines['balance2']),digits=get_digits(dp='Account'))}</td>
		</tr>
	%endif
	
%endfor
<% total_asset += lv3_total %>
<% total_asset2 += lv3_total2 %>
<tr>
	<td>&nbsp</td>
	<td colspan="2"></td>
	<td></td>
	<td></td>
	<td></td>
</tr>
<tr>
	<td></td>
	<td colspan="2">Total ${lv3_name}</td>
	<td></td>
	<td style="text-align: right">${formatLang(int(lv3_total),digits=get_digits(dp='Account'))}</td>
	<td style="text-align: right">${formatLang(int(lv3_total2),digits=get_digits(dp='Account'))}</td>
</tr>
<tr>
	<td colspan="6">&nbsp</td>
</tr>
<tr>
	<td colspan="6">&nbsp</td>
</tr>

<tr>
	<td colspan="4">&nbsp</td>
	<td style="text-align: right">${formatLang(int(total_asset),digits=get_digits(dp='Account'))}</td>
	<td style="text-align: right">${formatLang(int(total_asset2),digits=get_digits(dp='Account'))}</td>
</tr>














<% 
	lv3_name	= ""
	lv3_total	= 0.0
	total_liability = 0.0
	lv3_total2	= 0.0
	total_liability2 = 0.0
%>


<tr>
	<td></td>
	<td colspan="2" style="text-align: center">Liability & Equity</td>
	<td colspan="3"></td>
</tr>
<tr>
	<td colspan="6">&nbsp</td>
</tr>
%for lines in get_lines_another('liability'):
	
	%if lines['type'] == 'view' and lines['level'] == 3:
		<%level3_no+=1%>
		<%total_liability += lv3_total%>
		<%total_liability2 += lv3_total2%>
		%if lv3_name <> "":
			<tr>
				<td>&nbsp</td>
				<td colspan="2"></td>
				<td></td>
				<td></td>
				<td></td>
			</tr>
			<tr>
				<td></td>
				<td colspan="2">Total ${lv3_name}</td>
				<td></td>
				<td style="text-align: right">${formatLang(int(lv3_total),digits=get_digits(dp='Account'))}</td>
				<td style="text-align: right">${formatLang(int(lv3_total2),digits=get_digits(dp='Account'))}</td>
			</tr>
			<tr>
				<td colspan="6">&nbsp</td>
			</tr>
			<tr>
				<td colspan="6">&nbsp</td>
			</tr>
		%endif
		<tr>
			<td>${level3_no}</td>
			<td colspan="2">${lines['name']}</td>
		</tr>
		<tr>
			<td colspan="6">&nbsp</td>
		</tr>
		<% lv3_name =  lines['name']%>
		<% lv3_total =  lines['balance']%>
		<% lv3_total2 =  lines['balance2']%>
	%endif
	
	%if lines['type'] == 'view' and lines['level'] == 4:
		<tr>
			<td></td>
			<td width="40"></td>
			<td>${lines['name']}</td>
			<td></td>
			<td style="text-align: right">${formatLang(int(lines['balance']),digits=get_digits(dp='Account'))}</td>
			<td style="text-align: right">${formatLang(int(lines['balance2']),digits=get_digits(dp='Account'))}</td>
		</tr>
	%endif
%endfor
<%total_liability += lv3_total%>
<%total_liability2 += lv3_total2%>
<tr>
	<td>&nbsp</td>
	<td colspan="2"></td>
	<td></td>
	<td></td>
	<td></td>
</tr>
<tr>
	<td></td>
	<td colspan="2">Total ${lv3_name}</td>
	<td></td>
	<td style="text-align: right">${formatLang(int(lv3_total),digits=get_digits(dp='Account'))}</td>
	<td style="text-align: right">${formatLang(int(lv3_total2),digits=get_digits(dp='Account'))}</td>
</tr>
<tr>
	<td colspan="6">&nbsp</td>
</tr>
<tr>
	<td colspan="6">&nbsp</td>
</tr>
<tr>
	<td colspan="4">&nbsp</td>
	<td style="text-align: right">${formatLang(int(total_liability),digits=get_digits(dp='Account'))}</td>
	<td style="text-align: right">${formatLang(int(total_liability2),digits=get_digits(dp='Account'))}</td>
</tr>

</table>


</body>
</html>