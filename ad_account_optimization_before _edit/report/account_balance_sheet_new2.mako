<html>
<body>
${get_data(data)}
<% setLang('en_US' or 'en_ID' ) %>
<table width=100% border="1" cellscpacing="0" cellpadding="0" style="font-family:arial;font-size:12px";>
	<tr>
		<td colspan="4">Notes</td>
		<td>xxxxx</td>
		<td>yyyyy</td>
	</tr>
<%
	level3_no = 0
	account_lvl3_name = "xxx"
%>
%for lines in get_lines_another('asset'):
	
	%if lines['type'] == 'view' and lines['level'] == 2:
		<tr>
			<td></td>
			<td colspan="2" style="text-align: center">${lines['name']}</td>
			<td colspan="3"></td>
		</tr>
	%endif
	
	%if account_lvl3_name <> "xxx":
		<tr>
			<td></td>
			<td colspans="2">Total ${account_lvl3_name}</td>
			<td></td>
			<td></td>
			<td></td>
		</tr>
		account_lvl3_name = ""
	%endif
	
	%if lines['type'] == 'view' and lines['level'] == 3:
		<%level3_no+=1%>
		
		<tr>
			<td>${level3_no}</td>
			<td colspan="5">${lines['name']}</td>
		</tr>
		<%account_lvl3_name = lines['name']%>
	%endif
	
	%if lines['type'] == 'view' and lines['level'] == 4:
		<tr>
			<td></td>
			<td width="40"></td>
			<td>${lines['name']}</td>
			<td>Notes</td>
			<td>${formatLang(int(lines['balance']),digits=get_digits(dp='Account'))}</td>
			<td></td>
		</tr>
	%endif
	
%endfor

</table>
</body>
</html>