<html>
	
	<head>
	<style type="text/css">
        table #head {
        	width:100%;
        }
        .list_table0 {
			font-size:18px;
			font-weight:bold;
			padding-top:10px;
			padding-bottom:10px;
			padding-right:15%;
			width:70%;
			border-collapse:collapse;
        	border-top:1px solid white;
        	border-bottom:1px solid white;
        	border-left:1px solid white;
		}
		.list_table1{
			width:100%;
			font-size:11px;
			border-left:1px solid black;
			border-top:1px solid black;
        	border-bottom:1px solid black;
        	border-right:1px solid black;
		}
		.list_table2 {
			font-size:10px;
		}
		.list_table3 {
			font-size:10px;
		}
		.list_table4 {
			font-size:10px;
			padding-top:5px;
			padding-bottom:5px;
		}
		.cust_info
			{
			font-size:10px;
			font-weight:bold;
			border-top:1px solid black;
			border-bottom:1px solid black;
			border-left:1px solid black;
			border-right:1px solid black;
			padding-top:6px;
			padding-bottom:6px;
			}
		.inv_line td
			{
			border-top:0px;
			border-bottom:1px solid black;
			}
    </style>
	<%
	import addons
	%>
	</head>
	<body>
		<% form=data['form'] %>
	    <hr size="2px" color="white">
		<center>
			<h3>Daftar Kehadiran Karyawan</h3>
			<h5>Bulan : ${time.strftime('%B', time.strptime(get_period(form['month_print']),'%Y-%m-%d'))}</h5>
		</center>
		<table width="100%" class="list_table1" cellpadding="3">
			<tr>
				<th bgcolor="#CCCCCC" align="center"><b>No</b></th>
				<th bgcolor="#CCCCCC" align="center"><b>NIK</b></th>
				<th bgcolor="#CCCCCC" align="center"><b>Name</b></th>
				<th bgcolor="#CCCCCC" align="center"><b>Day</b></th>
				<th bgcolor="#CCCCCC" align="center"><b>Sign In</b></th>
				<th bgcolor="#CCCCCC" align="center"><b>Sign Out</b></th>
				<th bgcolor="#CCCCCC" align="center"><b>Total Jam</b></th>
				<th bgcolor="#CCCCCC" align="center"><b>Keterangan</b></th>
			</tr>
			<% n=1 %>
			%for emp in get_employee(form['employee_ids']):
				<tr>
					<td bgcolor="#CCCFFF">${ n }</td>
					<td bgcolor="#CCCFFF">${ emp.nik }</td>
					<td bgcolor="#CCCFFF">${ emp.name }</td>
					<td bgcolor="#CCCFFF"> </td>
					<td bgcolor="#CCCFFF"> </td>
					<td bgcolor="#CCCFFF"> </td>
					<td bgcolor="#CCCFFF"> </td>
					<td bgcolor="#CCCFFF"> </td>
				</tr>
				%if get_work_time_monthly(emp.id, form['month_print']):
					%for worktime in get_work_time_monthly(emp.id, form['month_print']):
						%if worktime['name'] in ['Sabtu','Minggu']:
							<% bg = "yellow" %>
						%else:
							<% bg = "" %>
						%endif
						<tr class="inv_line">
							<td> </td>
							<td> </td>
							<td> </td>
							<td align="left" bgcolor=${bg}>${ worktime['name'] }, ${ worktime['day'] and time.strftime('%d-%m-%Y', time.strptime(worktime['day'],'%Y-%m-%d')) or '' }</td>
							<td align="center" bgcolor=${bg}>${ worktime['sign_in'] and time.strftime('%H:%M:%S', time.strptime(worktime['sign_in'],'%Y-%m-%d %H:%M:%S'))  or '' }</td>
							<td align="center" bgcolor=${bg}>${ worktime['sign_out'] and time.strftime('%H:%M:%S', time.strptime(worktime['sign_out'],'%Y-%m-%d %H:%M:%S'))  or '' }</td>
							<td align="right" bgcolor=${bg}>${ worktime['total'] or '' }</td>
							<td bgcolor=${bg}>${ worktime['sign_in'] and 'Hadir' or ''}</td>
						</tr>
					%endfor
				%else:
					<td> </td>
					<td> </td>
					<td> </td>
					<td align="center">-</td>
					<td align="center">-</td>
					<td align="center">-</td>
					<td align="center">00:00:00</td>
					<td>Tidak Hadir</td>
				%endif
				<%n+=1%>
				</tr>
			%endfor
			
		</table>
	</body>
</html>
