import React, { useState, useEffect, useRef } from 'react';
import { ChevronDown, ChevronUp, Users, Clock, Calendar, ChevronLeft, ChevronRight, AlertCircle, ExternalLink, Mail, Phone, MapPin } from "lucide-react";
import { Link } from 'react-scroll';
import { motion, AnimatePresence } from 'framer-motion';


export function HomeSection() {
  // Optional prop for aspect ratio control
  // 
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  
  const images = [
    "https://cdn.glitch.global/f6cf5324-6f29-4927-81d0-f904b3b236c3/Batch%205-PP(BOI)group%20photo%20R_page-0001.jpg?v=1744866716861",
    "https://cdn.glitch.global/f6cf5324-6f29-4927-81d0-f904b3b236c3/WhatsApp%20Image%202025-04-17%20at%2010.35.21%20AM.jpeg?v=1744866470246",
    "https://cdn.glitch.global/f6cf5324-6f29-4927-81d0-f904b3b236c3/WhatsApp%20Image%202025-04-17%20at%2010.49.14%20AM.jpeg?v=1744867185183",
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex((prevIndex) => (prevIndex + 1) % images.length);
    }, 5000);
    return () => clearInterval(interval);
  }, [images.length]);

  useEffect(() => {
    setIsLoading(true);
    const img = new Image();
    img.src = images[currentImageIndex];
    img.onload = () => {
      setIsLoading(false);
    };
  }, [currentImageIndex]);

  const goToPreviousSlide = () => {
    setCurrentImageIndex((prevIndex) => (prevIndex - 1 + images.length) % images.length);
  };
  
  const goToNextSlide = () => {
    setCurrentImageIndex((prevIndex) => (prevIndex + 1) % images.length);
  };
  
  return (
    <div className="w-full min-h-screen flex items-center justify-center">
      <motion.div
        className="relative w-full h-screen max-h-screen overflow-hidden"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.5 }}
      >
        <div className="relative w-full h-full">
          <AnimatePresence mode="wait">
            <motion.div
              key={images[currentImageIndex]}
              className="absolute inset-0 w-full h-full"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5 }}
            >
              <div className="w-full h-full flex items-center justify-center bg-gray-100">
                <img
                  src={images[currentImageIndex]}
                  alt={`Slide ${currentImageIndex + 1}`}
                  className={`w-full h-full object-cover md:object-cover ${isLoading ? 'opacity-0' : 'opacity-100'} transition-opacity duration-300`}
                  style={{
                    objectPosition: 'center center'
                  }}
                />
              </div>
            </motion.div>
          </AnimatePresence>
          
          {/* Dark overlay for better visibility of controls */}
          <div className="absolute inset-0 bg-black bg-opacity-20 pointer-events-none" />
          
          {/* Navigation buttons */}
          <div className="absolute inset-0 flex items-center justify-between p-4 md:p-6">
            <button 
              onClick={goToPreviousSlide}
              className="bg-white/30 backdrop-blur-sm p-2 rounded-full shadow-md hover:bg-white/50 transition-all z-10"
              aria-label="Previous slide"
            >
              <ChevronLeft className="w-6 h-6 text-gray-800" />
            </button>
            <button 
              onClick={goToNextSlide}
              className="bg-white/30 backdrop-blur-sm p-2 rounded-full shadow-md hover:bg-white/50 transition-all z-10"
              aria-label="Next slide"
            >
              <ChevronRight className="w-6 h-6 text-gray-800" />
            </button>
          </div>
          
          {/* Indicators */}
          <div className="absolute bottom-8 left-0 right-0 flex justify-center gap-2 z-10">
            {images.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentImageIndex(index)}
                className={`w-3 h-3 rounded-full transition-all ${currentImageIndex === index ? 'bg-white w-6' : 'bg-white/50'}`}
                aria-label={`Go to slide ${index + 1}`}
              />
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
}

// CoursesList Component
export function CoursesList() {
  const [expandedCourse, setExpandedCourse] = useState(null);

  const courses = [
    {
      course: 1,
      title: "ARVR Govt. Official Training - Advanced",
      objective: "Focuses on hands-on AR experience using Unity and Vuforia, suitable for those with some Unity knowledge.",
      speakers: ["Dr. Sarwan Singh", "Mr. Nikshep Paliwal, Mr. Amrinder Singh"],
      days: [
        {
          
          theory: {
            title: "GOT – Advanced (40 Hours)",
            topics: ["Unity Advanced Features (8 hrs)", "Complex AR with Vuforia (10 hrs)",  "Interactive VR with A-Frame (10 hrs)","Cross-Platform Testing & Optimization (6 hrs)","Capstone Project (6 hrs)"],
          },
          
        },
        // ... (rest of the course data - truncated for brevity)
      ],
    },
    {
      course: 2,
      title: "ARVR Govt. Official Training - Basic",
      objective: "Perfect for beginners to explore AR/VR fundamentals and get started with Unity.",
      speakers: ["Dr. Sarwan Singh", "Mr. Nikshep Paliwal, Mr. Amrinder Singh"],
      days: [
        {
          day: 1,
          theory: {
            title: "GOT – Basic (30 Hours)",
            topics: ["Introduction to AR/VR (4 hrs)","Getting Started with Unity (6 hrs)","Building AR Experiences with Vuforia (10 hrs)","Introduction to WebVR using A-Frame (6 hrs)","Capstone Project (4 hrs)"],
          },
          
        },
        // ... (rest of the course data - truncated for brevity)
      ],
    },
    {
      course: 3,
      title: "ARVR Bootcamp",
      objective: "An intensive, fast-paced version covering all modules from basics to project in a compact timeline.",
      speakers: ["Dr. Sarwan Singh", "Mr. Nikshep Paliwal, Mr. Amrinder Singh"],
      days: [
        {
          day: "Topic Covered",
          theory: {
            title: "Bootcamp (40 Hours)",
            topics: ["Unity Basics + Environment Design (8 hrs)","Rapid AR Prototyping with Vuforia (10 hrs)","Real-World Simulations using A-Frame (10 hrs)","Multi-device Deployment Techniques (6 hrs)","Capstone Project (6 hrs)"],
          },
          
        },
        // ... (rest of the course data - truncated for brevity)
      ],
    },
    {
  "course": 4,
  "title": "BDDS Govt. Official Training - Advanced",
  "objective": "Build a strong mathematical and practical foundation in deep learning",
  "speakers": ["Dr. Sarwan Singh", "Mr. Lovnish Verma", "Mr. Ravi Kant"],
  "days": [
    {
      "day": 1,
      "theory": {
        "title": "GOT – Advanced (40 Hours)",
        "topics": [
          "Introduction to Big Data: Characteristics, Sources, and Value",
          "Hadoop Ecosystem Overview: HDFS, YARN, MapReduce",
          "Apache Hive: Data Warehousing Concepts",
          "Apache Sqoop and Flume: Data Ingestion Techniques",
          "Apache Spark: Architecture, RDDs vs DataFrames",
          "Spark SQL and Integration with Hive",
          "NoSQL Concepts: Types and Use Cases",
          "MongoDB Overview: Document Store, CRUD Operations, Indexing",
          "Python for Data Science: Numpy, Pandas Overview",
          "Statistical Analysis for Data Science",
          "Data Visualization: Matplotlib, Seaborn, ggplot",
          "Machine Learning Concepts: Supervised & Unsupervised Learning",
          "Algorithms: Linear/Logistic Regression, Decision Trees, K-Means, Association Rules",
          "Neural Networks: Architecture, Gradient Descent, Activation Functions",
          "Deep Learning Frameworks: TensorFlow and Keras",
          "Introduction to CNNs and RNNs",
          "Applications of AI in Government and Public Sectors",
          "OpenAI Overview and Industry Trends",
          "Capstone Planning: Problem Selection, Data Sources, and Design",
          "Evaluation Criteria and Report Preparation"
        ]
      },
      "practical": {
        "title": "Setting Up the Environment",
        "topics": [
          "Install and Configure Hadoop Single Node Cluster",
          "Run Word Count Program using MapReduce on HDFS Data",
          "Data Loading in Hive and Basic Query Execution",
          "Sqoop Import from MySQL to HDFS/Hive",
          "Log Data Collection using Apache Flume",
          "Create RDDs and DataFrames in Apache Spark using PySpark",
          "Use Spark SQL to Transform and Query Data",
          "Setup MongoDB and Create a TODO CRUD Application",
          "Data Manipulation with Pandas: Filtering, Grouping, Aggregation",
          "Numerical Computations with NumPy Arrays",
          "Generate Charts using Matplotlib and Seaborn",
          "Preprocess Real-World Dataset (e.g., missing values, encoding)",
          "Build ML Models using Scikit-Learn (Regression, Classification)",
          "Train and Evaluate a Neural Network using Keras (ANN)",
          "Create a Simple CNN for Image Classification (e.g., MNIST)",
          "Train an RNN/LSTM for Time Series or Text Data",
          "Use TensorBoard to Visualize Training Metrics",
          "Integrate Model with a Web App (Optional Demo)",
          "Work on Capstone Project Tasks: Data Ingestion, Cleaning, EDA",
          "Submit Initial Capstone Proposal and Progress Snapshot"
        ]
      }
    }
  ]
},
   {
  "course": 5,
  "title": "BDDS Govt. Official Training - Basic",
  "objective": "Build a strong mathematical and practical foundation in deep learning",
  "speakers": ["Dr. Sarwan Singh", "Mr. Lovnish Verma", "Mr. Ravi Kant"],
  "days": [
    {
      "day": 1,
      "theory": {
        "title": "GOT – Basic (30 Hours)",
        "topics": [
          "Introduction to Databases: RDBMS vs NoSQL",
          "What is Big Data? Volume, Velocity, Variety, Veracity, and Value",
          "Introduction to Data Science: Scope and Applications",
          "What is Deep Learning? History and Real-World Use Cases",
          "Overview of Data Engineering and Data Analytics Roles",
          "Introduction to Hadoop Ecosystem and Architecture",
          "Understanding HDFS (Hadoop Distributed File System)",
          "Introduction to YARN and Resource Management",
          "Need for Distributed Storage and Processing",
          "Difference between OLAP and OLTP Systems"
        ]
      },
      "practical": {
        "title": "Setting Up the Environment",
        "topics": [
          "Installing Python and Jupyter Notebook (Anaconda)",
          "Installing and Configuring Java and Hadoop (Single Node)",
          "Basic Linux Commands for Hadoop Operations",
          "Running First MapReduce Example (Word Count)",
          "Working with Jupyter: Creating First Notebook",
          "Importing Python Libraries: NumPy, Pandas, Matplotlib, Seaborn",
          "Exploring a Sample CSV Dataset using Pandas",
          "Performing Basic Statistics (mean, median, std) on Data",
          "Installing MongoDB and Running First Insert/Find Query",
          "Case Study: Review of Public Sector Data Use Cases"
        ]
      }
    }
  ]
},

   {
  "course": 6,
  "title": "BDDS Bootcamp",
  "objective": "Build a strong mathematical and practical foundation in deep learning",
  "speakers": ["Dr. Sarwan Singh", "Mr. Lovnish Verma", "Mr. Ravi Kant"],
  "days": [
    {
      "day": 1,
      "theory": {
        "title": "Bootcamp (40 Hours)",
        "topics": [
          "What is Big Data? – 5Vs and Applications",
          "Introduction to Data Science – Definitions, Scope, and Industry Use Cases",
          "Introduction to Relational Databases and DBMS Concepts",
          "Basics of SQL – SELECT, INSERT, UPDATE, DELETE Commands",
          "Understanding Joins – INNER, LEFT, RIGHT, FULL",
          "Constraints and Normalization in SQL",
          "Introduction to Hadoop – History, Architecture and Ecosystem",
          "HDFS and YARN – Storage and Resource Management",
          "Understanding the MapReduce Programming Model",
          "Overview of ETL Process and Data Pipelines"
        ]
      },
      "practical": {
        "title": "Setting Up the Environment",
        "topics": [
          "Installing Python, TensorFlow, PyTorch via Anaconda",
          "Setting up Jupyter Notebook for Development",
          "Installing Java and Hadoop on Ubuntu VM (Single Node Cluster)",
          "Running Initial HDFS Commands and Understanding HDFS Shell",
          "Executing Sample MapReduce Jobs (Word Count)",
          "Installing and Querying with Apache Hive",
          "Hands-on SQL Practice – SELECT, JOINs, GROUP BY, HAVING",
          "Installing and Running MongoDB Locally",
          "Performing CRUD Operations in MongoDB",
          "Creating First DataFrame using Pandas and Plotting with Matplotlib"
        ]
      }
    }
  ]
}

  ];

  const toggleCourse = (courseNumber) => {
    setExpandedCourse(expandedCourse === courseNumber ? null : courseNumber);
  };

  return (
    <motion.section
      id="courses-section"  // Changed from home-section to courses-section
      className="py-16 bg-gray-100"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <motion.h2
            className="text-3xl font-bold text-gray-900 sm:text-4xl mb-4"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.5 }}
          >
            Our Offered Courses
          </motion.h2>
          <motion.p
            className="text-lg text-gray-600"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.5 }}
          >
            Explore our comprehensive training programs
          </motion.p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {courses.map((courseItem) => (
            <motion.div
              key={courseItem.course}
              className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: courseItem.course * 0.1 }}
            >
              <div className="p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{courseItem.title}</h3>
                <p className="text-gray-600 text-sm mb-3">{courseItem.objective}</p>
                <div className="flex items-center text-gray-700 text-sm mb-2">
                  <Users className="mr-2" />
                  {courseItem.speakers.join(', ')}
                </div>
                {courseItem.days.length > 0 && (
                  <motion.div className="mt-3 overflow-hidden">
                    <button
                      onClick={() => toggleCourse(courseItem.course)}
                      className="text-blue-600 hover:text-blue-800 font-medium focus:outline-none flex items-center"
                    >
                      Course Details
                      {expandedCourse === courseItem.course ? <ChevronUp className="ml-1" /> : <ChevronDown className="ml-1" />}
                    </button>
                    <AnimatePresence>
                      {expandedCourse === courseItem.course && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.3 }}
                          className="mt-2"
                        >
                          {courseItem.days.map((day) => (
                            <div key={day.day} className="mb-2 border-t pt-2">
                              <h4 className="text-lg font-semibold text-gray-800">Topic Covered</h4>
                              {day.theory && (
                                <div className="mt-1">
                                  <p className="font-medium text-gray-700">{day.theory.title}:</p>
                                  <ul className="list-disc list-inside text-gray-600 text-sm">
                                    {day.theory.topics.map((topic, index) => (
                                      <li key={index}>{topic}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              {day.practical && (
                                <div className="mt-1">
                                  <p className="font-medium text-gray-700">{day.practical.title}:</p>
                                  <ol className="list-disc list-inside text-gray-600 text-sm">
                                    {day.practical.topics.map((topic, index) => (
                                      <li key={index}>{topic}</li>
                                    ))}
                                  </ol>
                                </div>
                              )}
                            </div>
                          ))}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.section>
  );
}


// Speakers Component
export function Speakers() {
  const speakers = [
    {
      name: "Sh. Deepak Wasan",
      role: "Executive Director",
      institution: "NIELIT Chandigarh",
      topic: "Artificial Intelligence and Machine Learning",
      bio: "Sh. Deepak Wasan specializes in Artificial Intelligence and Machine Learning, contributing significantly to the field through research and publications.",
      imageUrl: "https://cdn.glitch.global/9cb596b5-c24a-4aeb-9c0f-caf24928f45b/src%2Fcomponents%2Fed%20sir.png?v=1746525204364",
    },
    {
      name: "Ms. Anita Budhiraja",
      role: "Scientist-E",
      institution: "NIELIT Chandigarh",
      topic: "Artificial Intelligence and Machine Learning",
      bio: "Ms. Anita Budhiraja specializes in Artificial Intelligence and Machine Learning, contributing significantly to the field through research and publications.",
      imageUrl: "https://cdn.glitch.global/9cb596b5-c24a-4aeb-9c0f-caf24928f45b/download.png?v=1746525502415",
    },
    {
      name: "Dr. Sarwan Singh",
      role: "Scientist -D",
      institution: "NIELIT Chandigarh",
      topic: "Artificial Intelligence and Machine Learning",
      bio: "Dr. Sarwan Singh specializes in Artificial Intelligence and Machine Learning, contributing significantly to the field through research and publications.",
      imageUrl: "https://cdn.glitch.global/9cb596b5-c24a-4aeb-9c0f-caf24928f45b/sarwan%20sir.jpg?v=1746524544024",
    },
    {
      name: "Dr. Sharmistha Bhattacharjee",
      role: "Scientist-D",
      institution: "NIELIT Chandigarh",
      topic: "Advancements in Big Data & Data Science",
      bio: "Dr. Sharmistha Bhattacharjee brings extensive experience from the industry, offering valuable insights into current trends and practices.",
      imageUrl: "https://cdn.glitch.global/9cb596b5-c24a-4aeb-9c0f-caf24928f45b/Dr%20Sharmistha%20Bhattacharjee.png?v=1747199697156",
    },
    {
      name: "Mr. Lovnish Verma",
      role: "Project Engineer",
      institution: "NIELIT Chandigarh",
      topic: "Advancements in AI",
      bio: "Mr. Lovnish Verma works at NIELIT Chandigarh, focusing on advancements in Artificial Intelligence and Machine Learning.",
      imageUrl: "https://cdn.glitch.global/9cb596b5-c24a-4aeb-9c0f-caf24928f45b/LOVNISH%20PHOTO.jpg?v=1746523929925",
    },
    {
      name: "Mr. Nikshep Paliwal",
      role: "Project Engineer",
      institution: "NIELIT Chandigarh",
      topic: "AR/VR with expertise in Mobile Application Development",
      bio: "Mr. Nikshep Paliwal works at NIELIT Chandigarh, specializing in the AR/VR domain, actively involved in immersive technology development.",
      imageUrl: "https://cdn.glitch.global/9cb596b5-c24a-4aeb-9c0f-caf24928f45b/niks-removebg-preview.png?v=1746532376853",
    },
    {
      name: "Mr. Ravi Kant",
      role: "Project Assistant",
      institution: "NIELIT Chandigarh",
      topic: "Big Data & Data Science, Web Application Development,Graphic Design",
      bio: "Ravi Kant is a Project Assistant at NIELIT Chandigarh with expertise in Big Data, Data Science, Web Development, and Graphic Design.",
      imageUrl: "https://cdn.glitch.global/9cb596b5-c24a-4aeb-9c0f-caf24928f45b/ravikant.jpg?v=1746526675448",
    },
    {
      name: "Mr. Amrinder Singh",
      role: "Project Assistant",
      institution: "NIELIT Chandigarh",
      topic: "AR/VR & Web Application Developer",
      bio: "Mr. Amrinder Singh works on machine learning projects at NIELIT Chandigarh.",
      imageUrl: "https://cdn.glitch.global/9cb596b5-c24a-4aeb-9c0f-caf24928f45b/amrinder.png?v=1746526658273",
    },
  ];

  return (
    <section className="py-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 sm:text-4xl">
            Meet Our Distinguished Speakers
          </h2>
          <p className="mt-4 text-xl text-gray-600">
            Learn from industry experts and academic leaders
          </p>
        </div>
        <div className="mt-16 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {speakers.map((speaker, index) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow-lg overflow-hidden transition-transform duration-300 hover:transform hover:scale-105"
            >
              <div className="w-64 h-64 mx-auto flex justify-center items-center overflow-hidden rounded-full mt-6">
                <img
                  src={speaker.imageUrl}
                  alt={speaker.name}
                  className="object-cover w-full h-full"
                />
              </div>
              <div className="p-6">
                <h3 className="text-xl font-semibold text-gray-900">
                  {speaker.name}
                </h3>
                <p className="mt-1 text-sm font-medium text-indigo-600">
                  {speaker.role}
                </p>
                <p className="mt-1 text-sm text-gray-500">
                  {speaker.institution}
                </p>
                <div className="mt-3">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800">
                    {speaker.topic}
                  </span>
                </div>
                <p className="mt-4 text-sm text-gray-600 line-clamp-3">
                  {speaker.bio}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}





// Alert component (Z0 in the original code)
const Alert = ({ children, className = "" }) => (
  <div
    className={`p-4 bg-red-100 border border-red-400 text-red-700 rounded-md flex items-center ${className}`}
  >
    {children}
  </div>
);

const RegistrationSection = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 py-16 bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 mb-4">
          Registration Details
        </h1>
        <p className="text-xl text-gray-600">
          FutureSkills PRIME
          <span className="font-bold"> (NIELIT Chandigarh)</span>
        </p>
      </div>

      {/* Alert for deadline */}
      <Alert className="mb-8 border-red-200 bg-red-50 transform hover:scale-102 transition-transform">
        <AlertCircle className="h-5 w-5 text-red-600 animate-pulse" />
        <div className="text-red-600 font-semibold ml-3">
          Last Date for Registration: 20th May 2025 (Hard Deadline)
        </div>
      </Alert>



      {/* How to Register */}
      <div className="bg-white rounded-xl shadow-lg p-8 mb-8 hover:shadow-xl transition-shadow">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          How to Register
        </h2>
        <div className="space-y-6">
          {[
            "Fill your Details in Google Form",
            "Upload Necessary Documents",
            "Fill and Submit the physical form at NIELIT Chandigarh",
          ].map((step, index) => (
            <div
              key={index}
              className="flex items-start group"
            >
              <span className="flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-full bg-blue-100 text-blue-600 font-bold mr-4 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                {index + 1}
              </span>
              <div className="text-gray-600 pt-2">
                {step}
                {index === 2 && (
                  <div className="mt-3">
                    <a
                      href="https://docs.google.com/forms/d/e/1FAIpQqOPSoLR4YA/viewform?usp=header"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      <ExternalLink className="w-4 h-4 mr-2" />
                      Register Now
                    </a>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Contact for Registration Queries */}
      <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          Contact for Registration Queries
        </h2>
        <div className="space-y-4">
          {[
            {
              icon: <Mail className="w-5 h-5" />,
              info: "nielitchdropar@gmail.com",
            },
            {
              icon: <Phone className="w-5 h-5" />,
              info: "9815621657",
            },
          ].map((contact, index) => (
            <div
              key={index}
              className="flex items-center text-gray-600 hover:text-blue-600 transition-colors"
            >
              <span className="text-blue-600 mr-3">{contact.icon}</span>
              <span className="font-medium">{contact.info}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};



// Assuming these components (kv, b0, Y0, K0, k0, X0) are defined elsewhere in your project
// For this example, I'll create simple placeholder components


function ContactSection() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-16">
      <div
        className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow"
      >
        <h2
          className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 mb-8"
        >
          Contact Information
        </h2>
        <div className="grid md:grid-cols-2 gap-8">
          <div className="bg-gray-50 rounded-xl p-6">
            <h3
              className="text-xl font-bold text-gray-900 mb-4 flex items-center"
            >
              Program Coordinators
            </h3>
            <div className="space-y-4">
              {[
                "Mrs. Anita Budhiraja (Coordinator)",
                "Dr. Sarwan Singh (Co-Coordinator)",
              ].map((coordinator, index) => (
                <div
                  key={index}
                  className="flex items-center p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow"
                >
                  <span className="text-gray-700 font-medium">{coordinator}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="bg-gray-50 rounded-xl p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              Get in Touch
            </h3>
            <div className="space-y-4">
              {[
                {
                  icon: <Mail className="w-5 h-5" />,
                  content: "nielitchdropar@gmail.com",
                },
                {
                  icon: <Phone className="w-5 h-5" />,
                  content: "8264098112",
                },
                {
                  icon: <MapPin className="w-5 h-5" />,
                  content:
                    "NIELIT ROPAR. Birla Farms, Bada Phull. Rupnagar 140001 (Punjab).",
                },
              ].map((contact, index) => (
                <div
                  key={index}
                  className="flex items-start p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-all hover:translate-x-1"
                >
                  <span className="text-blue-600 mr-3 flex-shrink-0">
                    {contact.icon}
                  </span>
                  <span className="text-gray-700">{contact.content}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}








export function AppNav() {
  const [scrolled, setScrolled] = useState(false);
  const [activeSection, setActiveSection] = useState('home-section');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [openAlumniPrograms, setOpenAlumniPrograms] = useState({});
  const [openCourseTypes, setOpenCourseTypes] = useState({});

  const navSections = [
    { name: 'Home', id: 'home-section' },
    { name: 'Courses', id: 'courses-section' },
    { name: 'Speakers', id: 'speakers-section' },
    { name: 'Registration', id: 'registration-section' },
    { name: 'Contact', id: 'contact-section' },
  ];

  const alumniData = {
    'Big Data and Data Science': {
      'Government Official Training - Advanced': ['Batch 1', 'Batch 2', 'Batch 3'],
      'Government Official Training - Basic': ['Batch 1', 'Batch 2', 'Batch 3'],
      'BDDS BOOTCAMP': ['Batch 1', 'Batch 2', 'Batch 3'],
    },
    'Augmented and Virtual Reality': {
      'Government Official Training - Advanced': ['Batch 1', 'Batch 2', 'Batch 3'],
      'Government Official Training - Basic': ['Batch 1', 'Batch 2', 'Batch 3'],
      'AVR BOOTCAMP': [
        'Batch 1', 'Batch 2', 'Batch 3', 'Batch 4', 'Batch 5', 'Batch 6',
        'Batch 7', 'Batch 8', 'Batch 9', 'Batch 10', 'Batch 11', 'Batch 12',
        'Batch 13', 'Batch 14', 'Batch 15', 'Batch 16', 'Batch 17', 'Batch 18',
        'Batch 19', 'Batch 20'
      ],
    },
  };

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
      const scrollPos = window.scrollY + 100;

      for (const section of navSections) {
        const el = document.getElementById(section.id);
        if (el) {
          const top = el.offsetTop;
          const bottom = top + el.offsetHeight;
          if (scrollPos >= top && scrollPos < bottom) {
            setActiveSection(section.id);
            break;
          }
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (e, id) => {
    e.preventDefault();
    const el = document.getElementById(id);
    if (el) {
      const offset = el.getBoundingClientRect().top + window.pageYOffset - 70;
      window.scrollTo({ top: offset, behavior: 'smooth' });
      setActiveSection(id);
      setMobileMenuOpen(false);
    }
  };

  const toggleProgram = (program) => {
    setOpenAlumniPrograms((prev) => ({
      ...prev,
      [program]: !prev[program],
    }));
  };

  const toggleCourseType = (program, type) => {
    const key = `${program}-${type}`;
    setOpenCourseTypes((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const abbreviate = (str) =>
    str
      .split(' ')
      .map((word) => word[0].toUpperCase())
      .join('');

  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleWheel = (event) => {
      if (dropdownRef.current && dropdownRef.current.contains(event.target)) {
        event.stopPropagation();
        event.preventDefault();
      }
    };

    if (dropdownOpen) {
      document.addEventListener('wheel', handleWheel, { passive: false });
    } else {
      document.removeEventListener('wheel', handleWheel);
    }

    return () => {
      document.removeEventListener('wheel', handleWheel);
    };
  }, [dropdownOpen]);

  const AlumniDropdown = ({ isMobile = false }) => (
    <div
      ref={dropdownRef}
      className={`${
        isMobile ? 'pl-4' : 'absolute top-full left-0 mt-2 bg-white border rounded-md shadow-lg p-4 z-50 w-80 max-h-72 overflow-y-auto'
      } text-sm text-gray-800`}
    >
      {Object.entries(alumniData).map(([program, types]) => (
        <div key={program} className="mb-3">
          <button
            onClick={() => toggleProgram(program)}
            className="font-semibold text-blue-600 w-full text-left"
          >
            {program}
          </button>
          {openAlumniPrograms[program] && (
            <ul className="pl-2 mt-1 space-y-1">
              {Object.entries(types).map(([type, batches]) => {
                const programAbbr = abbreviate(program);
                const typeAbbr = abbreviate(type);
                const key = `${program}-${type}`;
                return (
                  <li key={type}>
                    <button
                      onClick={() => toggleCourseType(program, type)}
                      className="text-gray-700 font-medium w-full text-left"
                    >
                      {type}
                    </button>
                    {openCourseTypes[key] && (
                      <ul className="grid grid-cols-3 gap-2 mt-2 pl-2 text-gray-600">
                        {batches.map((batch, idx) => {
                          const batchNum = batch.match(/\d+/)?.[0] || idx + 1;
                          const url = `https://futureskillsprime.glitch.me/${programAbbr}_${typeAbbr}_Batch${batchNum}.html`;

                          return (
                            <li key={idx} className="list-disc list-inside">
                              <a
                                href={url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="hover:underline text-blue-500"
                              >
                                {batch}
                              </a>
                            </li>
                          );
                        })}
                      </ul>
                    )}
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      ))}
    </div>
  );

  return (
    <nav className={`fixed w-full top-0 z-50 transition-all duration-300 ${scrolled ? 'bg-white/95 backdrop-blur-md shadow-lg text-gray-800' : 'bg-white/80 shadow-md text-gray-800'}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="text-blue-600 font-bold text-xl">
            <a href="/">FutureSkills PRIME</a>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navSections.map(section => (
              <a
                key={section.id}
                href={`#${section.id}`}
                onClick={e => scrollToSection(e, section.id)}
                className={`capitalize font-medium text-sm tracking-wide relative group transition-colors ${activeSection === section.id ? 'text-blue-600' : 'text-gray-700 hover:text-blue-600'}`}
              >
                {section.name}
                <span className={`absolute bottom-0 left-0 h-0.5 bg-blue-600 w-full transform transition-transform ${activeSection === section.id ? 'scale-x-100' : 'scale-x-0 group-hover:scale-x-100'}`} />
              </a>
            ))}

            {/* Alumni Dropdown (Desktop) */}
            <div
              className="relative group"
              onMouseEnter={() => setDropdownOpen(true)}
              onMouseLeave={() => setDropdownOpen(false)}
            >
              <button className="capitalize font-medium text-sm tracking-wide text-gray-700 hover:text-blue-600 flex items-center gap-1">
                Alumni ▾
              </button>
              {dropdownOpen && <AlumniDropdown />}
            </div>
          </div>

          {/* Mobile Toggle Button */}
          <div className="md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle navigation"
              className="p-2 text-gray-700 rounded-md hover:bg-gray-100 hover:text-blue-600"
            >
              {mobileMenuOpen ? (
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white shadow-lg px-4 py-3 space-y-2">
          {navSections.map(section => (
            <a
              key={section.id}
              href={`#${section.id}`}
              onClick={e => scrollToSection(e, section.id)}
              className={`block px-3 py-2 rounded-md text-base font-medium ${activeSection === section.id ? 'bg-blue-100 text-blue-600' : 'text-gray-700 hover:bg-gray-100 hover:text-blue-600'}`}
            >
              {section.name}
            </a>
          ))}

          {/* Alumni Dropdown (Mobile) */}
          <div className="pt-2 border-t">
            <div className="px-3 py-2 font-semibold text-gray-700">Alumni</div>
            <AlumniDropdown isMobile />
          </div>
        </div>
      )}
    </nav>
  );
}



// Main App Component that combines all components with section IDs
export default function App() {
  return (
    <div className="pt-16"> {/* Adding padding-top to account for fixed navbar */}
      <AppNav />
      
      {/* Home Section with Carousel at the very top */}
      <div id="home-section">
        {/* Hero Section / Home */}
        <div className="max-w-7xl mx-auto px-4 py-16 bg-gradient-to-b from-gray-50 to-white">
          {/* Carousel Component */}
          <HomeSection />

          {/* Header */}
          <div className="text-center mb-16 relative">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-transparent to-purple-50 opacity-70"></div>
            <div className="relative">
              <br>
              
              </br>
              <br></br>
              <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 mb-6">
                FutureSkills PRIME
              </h1>
              <p className="text-2xl text-gray-600 mb-8">
                Bridging the Industry Skill Gap <span className="font-bold">(NIELIT)</span>
              </p>
              <div className="flex justify-center gap-8 flex-wrap">
                <div className="flex items-center text-gray-700 bg-white px-6 py-3 rounded-full shadow-sm hover:shadow-md transition-all">
                  <Calendar className="w-5 h-5 mr-3 text-blue-500" />
                  <span className="font-medium">1 Week (5 Days)</span>
                </div>
                <div className="flex items-center text-gray-700 bg-white px-6 py-3 rounded-full shadow-sm hover:shadow-md transition-all">
                  <Clock className="w-5 h-5 mr-3 text-blue-500" />
                  <span className="font-medium">6 Hours Daily</span>
                </div>
              </div>
            </div>
          </div>

          {/* About the Program */}
          <div className="bg-white rounded-2xl shadow-xl p-10 mb-12 backdrop-blur-sm">
            <h2 className="text-3xl font-bold text-gray-900 mb-8 border-b pb-4">About the Program</h2>
            <p className="text-gray-600 mb-10 text-lg leading-relaxed">
              FutureSkills PRIME (Programme for Re-skilling/ Up-skilling of IT Manpower for Employability) is an industry focused scheme sponsored by the Ministry of Electronics and Information Technology (MeitY), Government of India, with the goal to build skills in the emerging 10 technologies in the field of Information Technology. (www.futureskillsprime.in) NIELIT Chandigarh is a Co-Lead Resource Centre for Big Data Analytics and Virtual Reality.
            </p>
          </div>
        </div>
      </div>
      
      {/* Other Sections */}
      <div id="courses-section">
        <CoursesList />
      </div>
      
      <div id="speakers-section">
        <Speakers />
      </div>
      
      <div id="registration-section">
        <RegistrationSection />
      </div>
      
      <div id="contact-section">
        <ContactSection />
      </div>
    </div>
  );
}
