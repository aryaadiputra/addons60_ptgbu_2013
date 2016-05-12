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
		<td style="text-align: center"></td>
	</tr>
	<tr>
		<td colspan="3" style="text-align: center"></td>
		<td style="text-align: center">Notes</td>
		<td style="text-align: center">Rp.</td>
		<td style="text-align: center"></td>
	</tr>
<%
	level3_no 	= 0
	lv3_name	= ""
	lv3_total	= 0.0
	total_income = 0.0
%>

%for lines in get_lines_another('income'):
	%if lines['type'] == 'view' and lines['level'] == 1:
		<tr>
			<td></td>
			<td colspan="2" style="text-align: center">${lines['name']}</td>
			<td colspan="3"></td>
		</tr>
		<tr>
			<td colspan="6">&nbsp</td>
		</tr>
	%endif
	%if lines['type'] == 'view' and lines['level'] == 2:
		<% level3_no+=1 %>
		<% total_income += lv3_total %>
		
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
				<td></td>
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
		
	%endif
	
	%if lines['type'] == 'view' and lines['level'] == 3:
		<tr>
			<td></td>
			<td width="40"></td>
			<td>${lines['name']}</td>
			<td></td>
			<td style="text-align: right">${formatLang(int(lines['balance']),digits=get_digits(dp='Account'))}</td>
			<td></td>
		</tr>
	%endif
	
%endfor
<% total_income += lv3_total %>

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
	<td></td>
</tr>
<tr>
	<td colspan="6">&nbsp</td>
</tr>
<tr>
	<td colspan="6">&nbsp</td>
</tr>

<tr>
	<td colspan="4">&nbsp</td>
	<td style="text-align: right">${formatLang(int(total_income),digits=get_digits(dp='Account'))}</td>
	<td></td>
</tr>










<% 
	lv3_name	= ""
	lv3_total	= 0.0
	total_expense = 0.0
%>


<tr>
	<td></td>
	<td colspan="2" style="text-align: center">Expense</td>
	<td colspan="3"></td>
</tr>
<tr>
	<td colspan="6">&nbsp</td>
</tr>
%for lines in get_lines_another('expense'):
	
	%if lines['type'] == 'view' and lines['level'] == 2:
		<%level3_no+=1%>
		<%total_expense += lv3_total%>
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
				<td></td>
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
		
	%endif
	
	%if lines['type'] == 'view' and lines['level'] == 3:
		<tr>
			<td></td>
			<td width="40"></td>
			<td>${lines['name']}</td>
			<td></td>
			<td style="text-align: right">${formatLang(int(lines['balance']),digits=get_digits(dp='Account'))}</td>
			<td></td>
		</tr>
	%endif
%endfor
<%total_expense += lv3_total%>

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
	<td></td>
</tr>
<tr>
	<td colspan="6">&nbsp</td>
</tr>
<tr>
	<td colspan="6">&nbsp</td>
</tr>
<tr>
	<td colspan="4">&nbsp</td>
	<td></td>
	<td>${formatLang(int(total_expense),digits=get_digits(dp='Account'))}</td>
</tr>




</table>


</body>
</html>