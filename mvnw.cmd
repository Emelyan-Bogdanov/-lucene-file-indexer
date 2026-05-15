@rem Maven Wrapper startup script for Windows
@rem Copyright 2007-2023 the original author or authors.
@rem
@rem Licensed under the Apache License, Version 2.0 (the "License");
@rem you may not use this file except in compliance with the License.
@rem You may obtain a copy of the License at
@rem
@rem      https://www.apache.org/licenses/LICENSE-2.0
@rem
@rem Unless required by applicable law or agreed to in writing, software
@rem distributed under the License is distributed on an "AS IS" BASIS,
@rem WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
@rem See the License for the specific language governing permissions and
@rem limitations under the License.

@if "%DEBUG%"=="" @echo off
@rem Set local scope for the variables
setlocal enabledelayedexpansion

set MAVEN_PROJECTBASEDIR=%CD%
set MAVEN_BASEDIR=%~dp0
set WRAPPER_JAR="%MAVEN_BASEDIR%\.mvn\wrapper\maven-wrapper.jar"
set WRAPPER_PROPERTIES="%MAVEN_BASEDIR%\.mvn\wrapper\maven-wrapper.properties"

@rem Resolve any "." and ".." in MAVEN_HOME to make it shorter.
for %%i in ("%MAVEN_BASEDIR%") do set MAVEN_HOME=%%~fi

@rem Download maven-wrapper.jar if not present
if not exist "%WRAPPER_JAR%" (
    echo Downloading maven-wrapper.jar...
    powershell -Command "Invoke-WebRequest -Uri https://repo1.maven.org/maven2/org/apache/maven/wrapper/maven-wrapper/3.2.0/maven-wrapper-3.2.0.jar -OutFile %WRAPPER_JAR%"
)

@rem Run the wrapper
"%JAVA_HOME%\bin\java.exe" -jar "%WRAPPER_JAR%" %*
if errorlevel 1 (
    echo Maven wrapper execution failed
    exit /b 1
)
