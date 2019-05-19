#include "opencv2/core.hpp"
#include <opencv2/core/utility.hpp>
#include "opencv2/highgui.hpp"
#include "opencv2/imgproc.hpp"
#include <stdio.h> 
#include <sys/socket.h> 
#include <stdlib.h> 
#include <netinet/in.h> 
#include <string.h>
#include <arpa/inet.h>
#include <iostream>
#include <thread>         // std::thread
#include <cstdlib>
#include <unistd.h>

#include "JsonParse.h"
 
using namespace cv;
using namespace std;

#define PORT 9999
#define DIVIDER 2.5

void doContour();
void getContours();
double getTheta(Point car, Point dst);

string imageName("/home/fxanhkhoa/Documents/theFxUITCar_Data/Snapshots/fx_UIT_Car.png");
Mat frame;
RNG rng(12345);
Mat edges, crop_img, gray, thresh;
vector<vector<Point> > contours;
vector<Vec4i> hierarchy;
vector<Vec2f> lines;
Point center;
double centerx;
JsonParse sATS;

#define BUFSIZE 1024

struct sockaddr_in address; 
int sock = 0, valread; 
struct sockaddr_in serv_addr; 
char *hello = "Hello from client"; 
char buffer[BUFSIZE];
char *json = new char[30];
int speed = 0, angle = 0;
int sendcount = 0;
int wait = 1;

void send_readFeedBack()
{
    int now_turn = 0;
    while (1)
    {
        if (now_turn == 0)
        {
            strcpy(sATS.request, "SPEED");
            //now_turn = 1;
        }
        else
        {
            strcpy(sATS.request, "ANGLE");
            now_turn = 0;
        }
        memset(json, 0, sizeof(json));
        json = sATS.GetJson();
        send(sock , json , strlen(json) , 0 );
        wait = 1;
        cout << "Size is: " << sizeof(buffer) << endl;
        valread = recv( sock , buffer, sizeof(buffer), 0);
        if (valread == -1){
            cout<<"BREAK";
            break;
        }
        cout << "VALREAD IS: " <<valread;
        if (strcmp("SPEED", sATS.request) == 0)
        {
            speed = atoi(buffer);
            cout << "SPEED = " << buffer <<endl;
            wait = 0;
        }
        else if (strcmp("ANGLE", sATS.request) == 0)
        {
            angle = atoi(buffer);
            cout << "ANGLE = " << buffer <<endl;
            wait = 0;
        }
    }
}


void process()
{
    int flag = 1;
    while (1)
    {
        frame = imread(imageName.c_str(), IMREAD_COLOR); // Read the file
        if( frame.empty() )                      // Check for invalid input
        {
            cout <<  "Could not open or find the image" << std::endl ;
            flag = 0;

        }
        // namedWindow( "Display window", CV_WINDOW_AUTOSIZE  ); // Create a window for display.
        // imshow( "Display window", frame );                // Show our image inside it.

        /*
        *Process here
        *
        */
        if (flag == 1){
            doContour();
            cout << "CURRENT SPEED IS:" << speed << endl;
        }

        if(waitKey(30) >= 0) break;
        flag = 1;
    }
}

int main( int argc, char** argv )
{
    cout << "OpenCV version : " << CV_VERSION << endl;
    cout << "Major version : " << CV_MAJOR_VERSION << endl;
    cout << "Minor version : " << CV_MINOR_VERSION << endl;
    cout << "Subminor version : " << CV_SUBMINOR_VERSION << endl;
    if( argc > 1)
    {
        imageName = argv[1];
    }
    if ( CV_MAJOR_VERSION < 3)
    {
        // Old OpenCV 2 code goes here. 
    } else
    {
        // New OpenCV 3 code goes here. 
    }

    
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) 
    { 
        printf("\n Socket creation error \n"); 
        return -1; 
    } 

    memset(&serv_addr, '0', sizeof(serv_addr)); 

    serv_addr.sin_family = AF_INET; 
    serv_addr.sin_port = htons(PORT); 
        
    // Convert IPv4 and IPv6 addresses from text to binary form 
    if(inet_pton(AF_INET, "172.17.0.1", &serv_addr.sin_addr)<=0)
    { 
        printf("\nInvalid address/ Address not supported \n"); 
        return -1; 
    } 

    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) 
    { 
        printf("\nConnection Failed \n"); 
        return -1; 
    }

    cout << "connected" << endl;
    // send(sock , hello , strlen(hello) , 0 );
    sATS.speed = 0;
    sATS.angle = 0;
    strcpy(sATS.request, "NONE");

    memset(json, 0, sizeof(json));

    // Parse to json String
    json = sATS.GetJson();

    thread readThread(send_readFeedBack);
    thread processThread(process);

    readThread.join();
    processThread.join();
}

void doContour(){
    resize(frame, frame, Size(800, 600));
    // Set region

    Rect roi;
    roi.x = 000;
    roi.y = 500;
    roi.width = 800;
    roi.height = 100;

    Point carPosition(400, 100);
    Point prvPosition = carPosition;

    // Crop with ROI
    crop_img = frame(roi);
    cvtColor(crop_img, gray, COLOR_BGR2GRAY);

    GaussianBlur(gray, gray, Size(15, 15), 1.5, 1.5);

    threshold(gray, thresh, 150, 255, THRESH_BINARY_INV);

    getContours();

    imshow("frame1", frame);
    imshow("vanishing", crop_img);
    imshow("frame", thresh);

    double theta = getTheta(carPosition, Point(centerx, 50));

    cout << theta << endl;

    //Set Angle
    sATS.angle = int(theta / DIVIDER);
    // Set Speed
    sATS.speed = 25;
}

void getContours(){
    findContours(thresh, contours, hierarchy, CV_RETR_TREE,
               CV_CHAIN_APPROX_SIMPLE, Point(0, 0));

    int dem = 0;
    centerx = 0; // Reset centerx
    Scalar color =
        Scalar(rng.uniform(0, 255), rng.uniform(0, 255), rng.uniform(0, 255));
    if (contours.size() > 0) {
        vector<Moments> mu(contours.size());
        Mat drawing = Mat::zeros(thresh.size(), CV_8UC3);
        for (int i = 0; i < contours.size(); i++) {
            double area = contourArea(contours[i]);
            double arclength = arcLength(contours[i], true);
            if (area > 25000) {
            dem++; //(Add number of contour)
            // Add moment point
            mu[i] = moments(contours[i], false);

            // Get Mass Center
            vector<Point2f> mc(contours.size());
            mc[i] = Point2f(mu[i].m10 / mu[i].m00, mu[i].m01 / mu[i].m00);
            centerx += mc[i].x;
            circle(drawing, mc[i], 4, color, -1, 8, 0);

            drawContours(drawing, contours, i, color, 2, 8, hierarchy, 0, Point());
            }
        }
        centerx = centerx / dem;
        circle(drawing, Point(centerx, 50), 4, color, -1, 8, 0);
        imshow("Contours", drawing);
    }
}

double getTheta(Point car, Point dst) {
  if (dst.x == car.x)
    return 0;
  if (dst.y == car.y)
    return (dst.x < car.x ? -90 : 90);
  // cout << "center x"<< dst.x << " ";
  double pi = acos(-1.0);
  double dx = dst.x - car.x;
  double dy = car.y - dst.y; // image coordinates system: car.y > dst.y
#if DEBUG
  cout << dx << " " << dy << endl;
#endif
  if (dx < 0)
    return -atan(-dx / dy) * 180 / pi;
  return atan(dx / dy) * 180 / pi;
}
