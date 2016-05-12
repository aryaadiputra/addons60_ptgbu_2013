<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
	<head>
		<style type="text/css">
			table
				{
				border-collapse:collapse;
				}
			table, td, tr, th
				{
				border:1px solid black;
				}
			th {font-size:14px;}
			td {font-size:12px;}
			td.curr
				{
				text-align:right;
				}
			td.curr_total
				{
				text-align:right;
				background-color:black;
				color: white;
				font-weight:bold;
				}
			td.line
				{
				height: 400px;
				}
			.ttd
				{
				text-align:center;
				padding-bottom:80px;
				padding-top:30px;
				width:100%;
				border:0px solid black;
				}
			.nama
				{
				text-align:center;
				width:100%;
				font-weight:bold;
				border:0px solid black;
				}
			.noborder
				{
				border:0px solid white;
				}
		</style>
	</head>
	<body>
		<% setLang('id_ID' or 'en_US') %>
		%for o in get_object(data):
			<h2><center>IURAN DANA PENSIUN, ${get_periode(o.period)}</center></h2>
		%endfor
		<table width=100% height="100%">
			<tr bgcolor=#BFBFBF>
				<th rowspan=3>No</th>
				<th rowspan=3>Nama</th>
				<th rowspan=3>L/P</th>
				<th rowspan=3>Jabatan</th>
				<th rowspan=3>Tanggal Lahir</th>
				<th rowspan=3>Upah Pokok</th>
				<th colspan=2>Iuran</th>
			</tr>
			<tr bgcolor=#BFBFBF>
				<th>Perusahaan</th>
				<th>Pekerja</th>
			</tr>
			<tr bgcolor=#BFBFBF>
				<th>6%</th>
				<th>2%</th>
			</tr>
			<% c=1 %>
			<% perusahaan=0 %>
			<% pekerja=0 %>
			%for o in get_object(data):
				%for e in o.employee:
					%if get_payslip(o,e):
						<tr>
							<td align='center'>${c}</td>
							<td>${e.name}</td>
							<td align='center'>${get_gender(e.gender)}</td>
							<td>${e.job_id.name}</td>
							<td>${get_birthday(e.birthday)}</td>
							<td class='curr'>${formatLang(int(get_payslip(o,e).basic),digits=get_digits(dp='Sale Price'))} Rp</td>
							<td class='curr'>${formatLang(int(get_payslip(o,e).basic*0.06),digits=get_digits(dp='Sale Price'))} Rp</td>
							<td class='curr'>${formatLang(int(get_payslip(o,e).basic*0.02),digits=get_digits(dp='Sale Price'))} Rp</td>
						</tr>
						<% c=c+1 %>
						<% perusahaan+=get_payslip(o,e).basic*0.06 %>
						<% pekerja+=get_payslip(o,e).basic*0.02 %>
					%endif
				%endfor
				<tr>
					<td colspan=6 align='right'><b>Iuran Bulanan &nbsp;&nbsp;&nbsp;&nbsp;</b></td>
					<td class='curr_total'>${formatLang(int(perusahaan),digits=get_digits(dp='Sale Price'))} Rp</td>
					<td class='curr_total'>${formatLang(int(pekerja),digits=get_digits(dp='Sale Price'))} Rp</td>
				</tr>
			%endfor
			
			<!--harus diperbaiki lagi lain waktu-->
			
		</table>
		<table width="100%" class="noborder">
			<tr class="noborder">
				<td class="ttd noborder">Disetujui Oleh</td>
			</tr>
			<tr class="noborder">
				<td class="nama noborder"><u>Danil Firdaus</u></td>
			</tr>
			<tr class="noborder">
				<td align="center" class="noborder">Manager SDM & Umum</td>
			</tr>
		</table>
	</body>
</html>