FROM tomcat:6.0

ADD ./fgdc2iso.war /usr/local/tomcat/webapps/
# Add a placeholder saxon-license.lic 
# visit http://www.saxonica.com/download/download.xml
RUN mkdir /etc/saxon-license/ && ln -s /etc/saxon-license/saxon-license.lic /etc/saxon-license.lic
