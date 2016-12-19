#include <iostream>
#include <string>
#include <vector>

const std::string capitalChatater[10] = { "零","壹","贰","叁","肆","伍","陆","柒","捌","玖" };
const std::string highRate[3] = { "万","亿","兆" };
const std::string ptrRate[4] = { "", "角","分","厘" };
std::vector<std::string> lowRate = { "","拾","佰","仟" };

std::string GetCapitalNumber(std::string orgStr);
std::string processInteger(std::string intStr);
std::string processInteger(std::string intStr);
std::string processPointNumber(std::string ptrStr);
std::string filterEmptyPosition(std::string numStr);
bool IsDividedPosition(const std::vector<std::string> &rtnVec, int idx);
void processZeroStr(std::string &numStr, std::string tempStr, std::string replace);

std::string GetCapitalNumber(std::string orgStr)
{
	std::string rtnStr;
	bool legalFlag = true;
	for (int j = 0; j < orgStr.size(); ++j)
	{
		if (orgStr[j] >= '0' && orgStr[j] <= '9'
			|| j == 0 && orgStr[0] == '-'
			|| orgStr[j] == '.')
		{
			legalFlag = true;
		}
		else
		{
			legalFlag = false;
			break;
		}
	}
	if (!legalFlag)
	{
		return "Cannot return the ammount in illegal format! ";
	}

	double orgNum = atof(orgStr.c_str());

	if (orgNum <= 1e-5 && orgNum >= -1e-5)
	{
		return "零元";
	}
	else if (orgNum < 1e-5)
	{
		return "Cannot return the ammount below 0! ";
	}


	int ptrIndex = orgStr.find('.');
	if (ptrIndex > 0)
	{
		//小数
		if (orgStr.find_first_of('.') != orgStr.find_last_of('.'))
		{
			return "Illegal format of num! " + orgStr;
		}
		else
		{
			std::string integerStr = orgStr.substr(0, ptrIndex);
			rtnStr = processInteger(integerStr);
			if (integerStr.size() <= 18)
			{
				rtnStr += processPointNumber(orgStr.substr(ptrIndex));
			}
		}
	}
	else if (ptrIndex == -1)
	{
		//整数
		rtnStr = processInteger(orgStr);
	}
	else
	{
		return "Cannot return the ammount in illegal format! ";
	}
	return rtnStr;
}

std::string processInteger(std::string intStr)
{
	if (intStr.size() > 18)
	{
		return "The ammount is too large! Please ensure the number is below 10^18!";
	}

	std::string rtnStr;
	std::vector<std::string> rtnVec;
	int adjustIdx = 0;
	int lastIndex = -1;
	for (int i = intStr.size() - 1; i >= 0; --i)
	{
		int capitalIdx = intStr[i] - '0';
		if (capitalIdx > 0)
		{
			if (lastIndex == 0)
			{
				rtnVec.push_back(capitalChatater[lastIndex]);
			}
		}

		if (intStr.size() - 1 - i == 4)
		{
			if (lastIndex == 0)
			{
				rtnVec.push_back(capitalChatater[lastIndex]);
			}
			rtnVec.push_back(highRate[0]);	//万
			adjustIdx += 4;
		}
		if (intStr.size() - 1 - i == 8)
		{
			if (lastIndex == 0)
			{
				rtnVec.push_back(capitalChatater[lastIndex]);
			}
			rtnVec.push_back(highRate[1]);	//亿
			adjustIdx += 4;
			lowRate.push_back("万");
		}
		if (intStr.size() - 1 - i == 13)
		{
			if (lastIndex == 0)
			{
				rtnVec.push_back(capitalChatater[lastIndex]);
			}
			rtnVec.push_back(highRate[2]);	//兆
			adjustIdx += 5;
			lowRate.push_back("亿");
		}

		if (capitalIdx > 0)
		{
			int lowIdx = intStr.size() - 1 - adjustIdx - i;
			if (lowIdx > 0 && lowIdx < lowRate.size())
			{
				rtnVec.push_back(lowRate[lowIdx]);
			}
			rtnVec.push_back(capitalChatater[capitalIdx]);
		}
		lastIndex = capitalIdx;

	}

	for (int i = rtnVec.size() - 1; i >= 0; i--)
	{
		if (rtnVec[i] == "零")
		{
			if (i == 0 || IsDividedPosition(rtnVec, i - 1))
			{
				continue;
			}
		}
		rtnStr += rtnVec[i];
	}
	return filterEmptyPosition(rtnStr);
}

std::string processPointNumber(const std::string ptrStr)
{
	std::string rtnStr;
	if (ptrStr.size() < 1)
	{
		return "";
	}
	else
	{
		if (ptrStr.size() == 1 || ptrStr[0] != '.')
		{
			std::cout << "Illegal format of point num! " << ptrStr << std::endl;
			return "";
		}
		else
		{
			for (int i = 1; i < ptrStr.size(); ++i)
			{
				int capitalIdx = ptrStr[i] - '0';
				if (i < ptrStr.size() - 1 || i == ptrStr.size() - 1 && capitalIdx != 0)
				{
					rtnStr += capitalChatater[capitalIdx];
					if (i < sizeof(ptrRate) / sizeof(ptrRate[0]))
					{
						rtnStr += ptrRate[i];
					}
				}
			}
		}
		return rtnStr;
	}
}


bool IsDividedPosition(const std::vector<std::string> &rtnVec, int idx)
{
	for (int i = 0; i < sizeof(highRate) / sizeof(highRate[0]); ++i)
	{
		if (rtnVec[idx] == highRate[i])
		{
			return true;
		}
	}
	return false;
}

std::string filterEmptyPosition(std::string numStr)
{
	if (numStr == "")
	{
		numStr = "零";
	}
	else
	{
		for (int i = 0; i < sizeof(highRate) / sizeof(highRate[0]); ++i)
		{
			processZeroStr(numStr, "零" + highRate[i - 1], "");// like "零万"
			processZeroStr(numStr, "零零", "零");// like "零零"
			if (i > 0)
			{
				processZeroStr(numStr, highRate[i] + highRate[i - 1], highRate[i]);// like "亿万"
			}
		}
	}
	return numStr += "元";
}

void processZeroStr(std::string &numStr, std::string tempStr, std::string replace)
{
	int idx = numStr.find(tempStr);
	if (idx >= 0)
	{
		numStr = numStr.replace(numStr.find(tempStr), tempStr.length(), replace);
	}
}

int main()
{
	std::string orgNum;
	std::cout << "请输入需要转换的数字：" << std::endl;
	std::cin >> orgNum;
	std::cout << "大写金额为：" << GetCapitalNumber(orgNum) << std::endl;
	system("PAUSE");
	return 0;
}
