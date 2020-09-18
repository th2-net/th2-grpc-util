# GRPC Generator Template
### Current supported languages: Java, Python
This tool is used to generate code from `.proto` files and upload constructed packages (`.proto` files with generated code) to specified repository
#### Build steps:
1. Create path `src/main/proto` in project root and store your `.proto` files here
2. Edit `publishing` section in `build.gradle` (by default it's published to `shared` dir in project root) file in order to specify the desired repository for Java code
3. Edit `twine upload...` step in `Dockerfile` in order to specify the desired repository for Python code. This is done by simply substitung parameters
#### `Publishing` section example for `build.gradle` file:
```publishing {
       publications {
           mavenJava(MavenPublication) {
               from components.java
   
               groupId = 'com.exactpro'
               artifactId = 'grpc-generator'
               version = '1.0'
   
           }
       }
       repositories {
           maven {
               name = "localRepo"
               url = sharedDir
           }
       }
   }