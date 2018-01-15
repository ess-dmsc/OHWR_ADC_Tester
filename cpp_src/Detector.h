/** Copyright (C) 2016, 2017 European Spallation Source ERIC */

/** @file
 *
 *  @brief Factory and Class for dynamically loadable detector types
 */

#pragma once
//#include <common/Trace.h>
#include <memory>
#include <string>
#include <vector>
#include <functional>
#include <thread>
#include <atomic>

struct ThreadInfo {
  std::function<void(void)> func;
  std::string name;
  std::thread thread;
};

class Detector {
public:
  using ThreadList = std::vector<ThreadInfo>;
  // default constructor, all instruments must implement these methods
  /** @brief generic pthread argument
   */
  Detector() = default;
  
  virtual ThreadList& GetThreadInfo() {
    return Threads;
  };

  virtual void StartThreads() {
    for (auto &tInfo : Threads) {
      tInfo.thread = std::thread(tInfo.func);
    }
  }
  
  virtual void StopThreads() {
    runThreads.store(false);
    for (auto &tInfo : Threads) {
      if (tInfo.thread.joinable()) {
        tInfo.thread.join();
      }
    }
  };
  /** @brief optional destructor */
  virtual ~Detector() {
    
  }

//  /** @brief document */
//  virtual int statsize() { return 0; }
//
//  /** @brief document */
//  virtual int64_t statvalue(size_t __attribute__((unused)) index) {
//    return (int64_t)-1;
//  }
//
//  /** @brief document */
//  virtual std::string &statname(size_t __attribute__((unused)) index) {
//    return noname;
//  }
//
//  virtual const std::string detectorname() { return "no detector"; }
protected:
  void AddThreadFunction(std::function<void(void)> &func, std::string funcName) {
    Threads.emplace_back(ThreadInfo{func, std::move(funcName)});
  };
  ThreadList Threads;
  std::atomic_bool runThreads{true};
private:
  
  std::string noname{""};
};

class DetectorFactory {
public:
  /** @brief creates the detector object. All instruments must implement this
  */
  virtual std::shared_ptr<Detector> create() = 0;
};
