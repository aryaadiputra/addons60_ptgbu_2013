<html>
	<head>
		<%
		import addons
		path=addons.get_module_resource("ad_hr_report/static/jquery-1.8.3.min.js")
		%>
		<script src="${path}" type="text/javascript"></script>
		
		<style>
			${css}
			table
				{
				border-collapse:collapse;
				border-color:lightGrey;
				}
			td
				{
				page-break-inside:avoid; 
				page-break-after:auto;
				}
			td.data {
				font-size:9px;
				height:30px;
				}
			td.tabhead
				{
				height:20px;
				font-size:10px;
				font-weight:bold;
				text-align:center;
				}
			td.group
				{
				height:21px;
				font-size:10px;
				font-weight:bold;
				background-color:lightGrey;
				}
			td.no{text-align:right; width:20px;}
			td.nik{text-align:left;width:40px;}
			td.name{text-align:left;width:150px;}
			td.adm{text-align:left;width:50px;}
			td.admd{text-align:center;width:80px;}
			td.job{text-align:left;width:200px;}
			td.lvl{text-align:right;width:30px;}
			td.wkp{text-align:left;width:59px;}
			
			td.nol{width:20px;}
			td.nikl{width:40px;}
			td.namel{width:150px;}
			td.adml{width:50px;}
			td.admdl{width:80px;}
			td.jobl{width:200px;}
			td.lvll{width:30px;}
			td.wkpl{width:59px;}	
		</style>
		<script>
			$(document).ready(function(){
				$('table:last-child').css('page-break-after',"auto");
			})
		</script>
	</head>
<body>
<center id="reportname" height="60 px">
	<h3 class="reportname">Employee List by Function</h3>
</center
<br height="30px;"/>
<% 
datalist=data['form']
dummy=False 
count=90
%>
<table border="1" bordercolor="lightGrey" cellpadding="3" cellspacing="0" style="page-break-after:always;">
	<tr style="page-break-inside:avoid; page-break-after:auto;">
		<td class="tabhead nol">No</td>
		<td class="tabhead nikl">NIK</td>
		<td class="tabhead namel">Name</td>
		<td class="tabhead adml">Admission</td>
		<td class="tabhead admdl">Admission Date</td>
		<td class="tabhead jobl">Job</td>
		<td class="tabhead lvll">Level</td>
		<td class="tabhead wkpl">Workplace</td>
	</tr>
	<%count+=33%>
	%for bagian in get_bagian():
		<% no=1 %>
		<tr style="page-break-inside:avoid; page-break-after:auto;">
			<td colspan="8" class="group">Bagian : ${bagian.title()}</td>
		</tr>
		<% dep_ids=[] %>
		%for x in get_dept(datalist['filter_dept'],dummy,bagian):
			<% dep_ids.append(x.id) %>
		%endfor
		
		<%count+=21%>
		<% employees=get_employee(datalist['active'],dep_ids,datalist['filter_sect'])%>
		%if employees>0:
			%for emp in employees:
				<tr style="page-break-inside:avoid; page-break-after:auto;">
					<td class="data no">${no}</td>
					<td class="data nik">${emp.nik}</td>
					<td class="data name">${emp.name}</td>
					<td class="data adm">${emp.admission_letter or "<center>N/A</center>"}</td>
					<td class="data admd">${emp.admission_date or "<center>N/A</center>"}</td>
					<td class="data job">${emp.job_id.name}</td>
					<td class="data lvl">${emp.current_job_level.name or "<center>N/A</center>"}</td>
					<td class="data wkp">${emp.work_location and emp.work_location.title() or "<center>N/A</center>"}</td>
				</tr>
				<% 
				count+=33
				no+=1
				%>
				%if ((count+40)>900):
					</table>
					<table style="page-break-after:always;" border="1" bordercolor="lightGrey" cellpadding="3" cellspacing="0">
						<tr style="page-break-inside:avoid; page-break-after:auto;">
							<td class="tabhead nol">No</td>
							<td class="tabhead nikl">NIK</td>
							<td class="tabhead namel">Name</td>
							<td class="tabhead adml">Admission</td>
							<td class="tabhead admdl">Admission Date</td>
							<td class="tabhead jobl">Job</td>
							<td class="tabhead lvll">Level</td>
							<td class="tabhead wkpl">Workplace</td>
						</tr>
					<% count=30 %>			
				%endif
			%endfor
		%endif
	%endfor

</table>
</body>
</html>