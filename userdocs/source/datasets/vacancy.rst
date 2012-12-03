Vacancies
=========

The Open Data Service imports advertised vacancy information from the central
recruitment portal at `https://www.recruit.ox.ac.uk/
<https://www.recruit.ox.ac.uk/>`_.

.. note ::

   Want to get started quickly?

   We've written `an example page <../_static/examples/vacancies-jquery.html>`_
   showing how to include a vacancy feed using jQuery and AJAX. You'll need  to
   change the references to ``31337175`` to the OxPoints ID for your unit,
   which you can find from the `main vacancies feeds page
   <https://data.ox.ac.uk/feeds/vacancies/>`_.


Feeds
-----

There are vacancy feeds for each unit at `https://data.ox.ac.uk/feeds/vacancies/
<https://data.ox.ac.uk/feeds/vacancies/>`_.

Feeds are available as Atom, RSS, RDF, XML and JSON. The latter three include
opening and closing dates, HTML and plain text descriptions, and details about
salary, contact, relevant unit and the building at which the job is based. The
RSS and Atom feeds only include a description, title, and a link.

Here's an example entry in an XML feed:

.. code-block:: xml

	<?xml version="1.0"?>
	<vacancies>
	  <vacancy id="105184">
	    <uri>https://data.ox.ac.uk/id/vacancy/105184</uri>
	    <url>https://data.ox.ac.uk/doc/vacancy/105184</url>
	    <webpage>https://www.recruit.ox.ac.uk/pls/hrisliverecruit/erq_jobspec_version_4.display_form?p_display_in_irish=N&amp;p_company=10&amp;p_refresh_search=Y&amp;p_process_type=&amp;p_recruitment_id=105184&amp;p_form_profile_detail=&amp;p_display_apply_ind=Y&amp;p_internal_external=E&amp;p_applicant_no=</webpage>
	    <label>Head of DARS Support Centre</label>
	    <opens>2012-11-07T10:14:50+00:00</opens>
	    <closes>2012-12-05T12:00:00+00:00</closes>
	    <location>Development Office/IT Services, University Offices/Hythe Bridge Street, Oxford</location>
	    <description format="application/xhtml+xml">&lt;div&gt;
	Live since 2009 and with a growing number of participants, the Development and Alumni Relations System for the collegiate University is critical to the next phase of Oxford&amp;#8217;s Campaign, which has an increased goal of &amp;#163;3bn, with over &amp;#163;1.4bn raised in new pledges and gifts since 2004. Envisioned to be both internally and externally recognised as the most advanced Higher Education fundraising system in Europe, DARS utilises Blackbaud CRM software and is a comprehensive tool for development and alumni relations professionals across the University, Colleges and Departments.&lt;br/&gt;&lt;br/&gt;This role will manage and have day-to-day operational responsibility for the DARS Support Centre, which incorporates more than twenty staff across the Development Office, Alumni Office and IT Services.  Its five teams provide functional, process and data, data migration, website and training support to promote, facilitate and drive the significant benefits for fundraising and alumni relations activity that can be achieved from a smarter collaborative approach to technology and to data for the collegiate University and for Oxonians and donors worldwide.&lt;br/&gt;&lt;br/&gt;This is an excellent opportunity for someone with a deep and broad understanding of relationship management business processes, backed with proven and significant experience working with and improving business systems in a complex and diverse organisation.  Exceptional negotiation and resource-planning skills are essential, coupled with the knowledge, astuteness and ability to achieve wide consensus when making decisions.&lt;br/&gt;&lt;br/&gt;Only applications received before 12.00 noon on 5 December 2012 can be considered. You will be required to upload a letter of application as part of your online application.  Interviews are currently scheduled to take place on Tuesday 11 December 2012.  It is anticipated that second interviews will take place on the afternoon of Monday 17 December 2012.
	&lt;/div&gt;
	</description>
	    <description format="text/plain">Live since 2009 and with a growing number of participants, the Development and Alumni Relations System for the collegiate University is critical to the next phase of Oxford’s Campaign, which has an increased goal of £3bn, with over £1.4bn raised in new pledges and gifts since 2004. Envisioned to be both internally and externally recognised as the most advanced Higher Education fundraising system in Europe, DARS utilises Blackbaud CRM software and is a comprehensive tool for development and alumni relations professionals across the University, Colleges and Departments.
	
	This role will manage and have day-to-day operational responsibility for the DARS Support Centre, which incorporates more than twenty staff across the Development Office, Alumni Office and IT Services.  Its five teams provide functional, process and data, data migration, website and training support to promote, facilitate and drive the significant benefits for fundraising and alumni relations activity that can be achieved from a smarter collaborative approach to technology and to data for the collegiate University and for Oxonians and donors worldwide.
	
	This is an excellent opportunity for someone with a deep and broad understanding of relationship management business processes, backed with proven and significant experience working with and improving business systems in a complex and diverse organisation.  Exceptional negotiation and resource-planning skills are essential, coupled with the knowledge, astuteness and ability to achieve wide consensus when making decisions.
	
	Only applications received before 12.00 noon on 5 December 2012 can be considered. You will be required to upload a letter of application as part of your online application.  Interviews are currently scheduled to take place on Tuesday 11 December 2012.  It is anticipated that second interviews will take place on the afternoon of Monday 17 December 2012.</description>
	    <organizationPart>
	      <uri>http://oxpoints.oucs.ox.ac.uk/id/31337175</uri>
	      <url>https://data.ox.ac.uk/doc:oxpoints/31337175</url>
	      <webpage>http://www.it.ox.ac.uk/</webpage>
	      <label>IT Services</label>
	      <address>
	        <street-address>16 Wellington Square</street-address>
	        <locality>Oxford</locality>
	        <postal-code>OX1 2HY</postal-code>
	      </address>
	    </organizationPart>
	    <basedNear>
	      <uri>http://oxpoints.oucs.ox.ac.uk/id/23233672</uri>
	      <url>http://oxpoints.oucs.ox.ac.uk/id/23233672</url>
	      <webpage>None</webpage>
	      <label>Beaver House</label>
	      <address>
	        <street-address>23-38 Hythe Bridge Street</street-address>
	        <locality>Oxford</locality>
	        <postal-code>OX1 2EP</postal-code>
	      </address>
	      <location>
	        <lat>51.753304</lat>
	        <long>-1.266764</long>
	      </location>
	    </basedNear>
	    <salary>
	      <label>Grade 9: £42,883 to £49,689, with discretionary range to £54,283</label>
	      <lower>42883</lower>
	      <upper>54283</upper>
	      <currency>GBP</currency>
	    </salary>
	    <contact>
	      <label>Personnel Assistant</label>
	      <email>recruitment@admin.ox.ac.uk</email>
	    </contact>
	  </vacancy>
	  …
	</vacancies>

Data
----

The data is updated hourly by scraping the recruitment site.


Limitations
-----------

At the moment the dataset doesn't include joint academic appointments listed at
http://www.ox.ac.uk/about_the_university/jobs/academic/, or college-only
vacancies.

The vacancies are matched to departments based on the free-text
location element just under the job title on recruit.ox. Occasionally
these get mismatched due to a typo, or because it wasn't quite
specific enough (e.g. when two units occupy the same building and only
the building name has been given).

If you notice that a job hasn't appeared, search for the vacancy ID at
https://data.ox.ac.uk/search/ to make sure it's been ingested. If it
has — and has been matched wrongly — contact opendata@oucs.ox.ac.uk to
get it fixed.


Examples of this dataset in use
-------------------------------

A number of departments are currently using vacancy feeds:

* `Department of Oncology <http://www.oncology.ox.ac.uk/opportunities>`_
* `Gray Institute for Radiation Oncology and Biology <http://www.rob.ox.ac.uk/opportunities>`_
* `IT Services <http://www.it.ox.ac.uk/about/jobs/>`_
