#include <iostream>
#include <cassert>
#include <exception>
using namespace std;

int main() {
	std::cerr << "ERROR!!\n";
	assert(false);
	throw std::runtime_error("PIZDA");
	string s;
	cin >> s;
	std::cout << s << endl;
	return -1;
}
