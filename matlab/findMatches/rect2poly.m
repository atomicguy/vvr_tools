function [xv, yv] = rect2poly(test_rectangle)

pointUL = [test_rectangle(1), test_rectangle(2) ];
pointLL = [test_rectangle(1), test_rectangle(2) + test_rectangle(4) ];
pointUR = [test_rectangle(1) + test_rectangle(3), test_rectangle(2) ];
pointLR = [test_rectangle(1) + test_rectangle(3), test_rectangle(2) + test_rectangle(4)];

xv = [pointLL(1), pointLR(1), pointUR(1), pointUL(1), pointLL(1)];
yv = [pointLL(2), pointLR(2), pointUR(2), pointUL(2), pointLL(2)];
end