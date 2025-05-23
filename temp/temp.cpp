#include <cstdlib>
#include <cstring>
#include <iostream>
#include <cctype>
#include <random>
#include <fstream>
// user-defined functions and procedures
int main() {
int num = 0;
int fact = 0;
int i = 0;
std::cout << "Enter a number:" << std::endl;
std::cin >> num;
fact = 1;
i = 1;
while ((i <= num)) {
fact = (fact * i);
i = (i + 1);
}
std::cout << "Factorial is:" << std::endl;
std::cout << fact << std::endl;
return 0;
}