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
			border-bottom:0px;
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
			<h3>Daftar Kehadiran Karyawan Harian</h3>
			<h5>${ time.strftime('%d/%m/%Y',time.strptime(form['date_print'],'%Y-%m-%d')) }</h5>
		</center>
		<table width="100%" class="list_table1" cellpadding="3">
			<tr>
				<td bgcolor="#CCCCCC">No</td>
				<td bgcolor="#CCCCCC">NIK</td>
				<td bgcolor="#CCCCCC">Name</td>
				<td bgcolor="#CCCCCC">Day</td>
				<td bgcolor="#CCCCCC">Sign In</td>
				<td bgcolor="#CCCCCC">Sign Out</td>
				<td bgcolor="#CCCCCC">Waktu Kehadiran</td>
				<td bgcolor="#CCCCCC">Status</td>
			</tr>
			<% n=1 %>
			%for emp in get_employee(form['employee_ids']):
				<tr>
				<td>${ n }</td>
				<td>${ emp.nik }</td>
				<td>${ emp.name }</td>
				%if get_work_time(emp.id, form['date_print']):
					%for worktime in get_work_time(emp.id, form['date_print']):
						%if worktime:
							<td>${ time.strftime('%d-%m-%Y', time.strptime(worktime['day'],'%Y-%m-%d %H:%M:%S'))  or '-' }</td>
							<td>${ time.strftime('%H:%M:%S', time.strptime(worktime['sign_in'],'%Y-%m-%d %H:%M:%S'))  or '-' }</td>
							<td>${ time.strftime('%H:%M:%S', time.strptime(worktime['sign_out'],'%Y-%m-%d %H:%M:%S'))  or '-' }</td>
							<td align="right">${ worktime['total'] or 0 }</td>
							<td>Hadir</td>
						%endif
					%endfor
				%else:
					<td align="center">-</td>
					<td align="center">-</td>
					<td align="center">-</td>
					<td align="right">00:00:00</td>
					<td>Tidak Hadir</td>
				%endif
				<%n+=1%>
				</tr>
			%endfor
			
		</table>
	</body>
</html>
