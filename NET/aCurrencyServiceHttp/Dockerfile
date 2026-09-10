FROM ubuntu:20.04
COPY . /app
WORKDIR /app

RUN uname -a
RUN apt -y update 
RUN apt -y install wget

# RUN wget http://ftp.us.debian.org/debian/pool/main/i/icu/libicu57_57.1-6+deb9u4_amd64.deb
# RUN dpkg -i libicu57_57.1-6+deb9u4_amd64.deb
#RUN wget https://packages.microsoft.com/ubuntu/22.04/prod/pool/main/
RUN wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb
RUN dpkg -i packages-microsoft-prod.deb

RUN apt -y update 
RUN apt -y install apt-transport-https 
RUN apt -y install dotnet-sdk-3.1 
RUN apt -y install dotnet-runtime-3.1 

RUN dotnet restore
RUN dotnet build
RUN dotnet publish -c Release -o out
RUN ls

EXPOSE 80/tcp
ENV ASPNETCORE_URLS http://localhost
ENV ASPNETCORE_ENVIRONMENT docker
 
#ENTRYPOINT dotnet run